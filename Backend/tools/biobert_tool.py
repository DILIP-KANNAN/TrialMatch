"""
BioBERT NLI Tool for TrialMatch 2.0.
Specialized semantic inference engine for clinical trial criteria entailment and contradiction.
"""

import os
import sys
from typing import Dict, Any, List, Optional

# Prevent transformers 5.x from choking on legacy torchvision 0.2.0
sys.modules['torchvision'] = None

import torch
import torch.nn.functional as F
from transformers import BertTokenizer, BertForSequenceClassification
import re

class BioBERTTool:
    """
    BioBERT Transfer Learning Tool.
    Uses fine-tuned weights on SNLI/Biomedical texts to evaluate Entailment (0), Neutral (1), Contradiction (2).
    """

    _instance = None
    _tokenizer = None
    _model = None
    _device = "cpu"
    _cache: Dict[str, Any] = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        # Determine model path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_dir, "biobert_nli_finetuned")

        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[BioBERTTool] Loading BioBERT NLI model on {self._device}...")

        try:
            if os.path.exists(model_path):
                self._tokenizer = BertTokenizer.from_pretrained(model_path)
                self._model = BertForSequenceClassification.from_pretrained(model_path)
                print(f"[BioBERTTool] Successfully loaded fine-tuned model from {model_path}.")
            else:
                raise FileNotFoundError(f"Model path {model_path} does not exist.")
        except Exception as e:
            print(f"[BioBERTTool] Warning: could not load fine-tuned model ({e}). Falling back to dmis-lab/biobert-base-cased-v1.1...")
            self._tokenizer = BertTokenizer.from_pretrained("dmis-lab/biobert-base-cased-v1.1")
            self._model = BertForSequenceClassification.from_pretrained("dmis-lab/biobert-base-cased-v1.1", num_labels=3)

        self._model.to(self._device)
        self._model.eval()

    def evaluate_pair(self, premise: str, hypothesis: str) -> Dict[str, Any]:
        """
        Evaluates premise vs hypothesis.
        Labels: 0 = Entailment, 1 = Neutral, 2 = Contradiction
        """
        cache_key = f"{premise.strip()}|||{hypothesis.strip()}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        inputs = self._tokenizer(
            premise,
            hypothesis,
            return_tensors="pt",
            truncation=True,
            max_length=128
        )
        inputs = {k: v.to(self._device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self._model(**inputs)
            logits = outputs.logits
            probs = F.softmax(logits, dim=-1).squeeze().tolist()

        if isinstance(probs, float):
            probs = [probs]

        # In standard 3-class SNLI head: 0: Entailment, 1: Neutral, 2: Contradiction
        p_entailment = float(probs[0]) if len(probs) > 0 else 0.0
        p_neutral = float(probs[1]) if len(probs) > 1 else 0.0
        p_contradiction = float(probs[2]) if len(probs) > 2 else 0.0

        pred_id = int(torch.argmax(logits, dim=-1).item())
        labels_map = {0: "Entailment", 1: "Neutral", 2: "Contradiction"}
        pred_label = labels_map.get(pred_id, "Neutral")

        confidence = max(p_entailment, p_neutral, p_contradiction)

        res = {
            "predicted_label": pred_label,
            "confidence": round(confidence, 4),
            "probabilities": {
                "entailment": round(p_entailment, 4),
                "neutral": round(p_neutral, 4),
                "contradiction": round(p_contradiction, 4)
            },
            "is_entailment": pred_label == "Entailment",
            "is_contradiction": pred_label == "Contradiction"
        }
        self._cache[cache_key] = res
        return res

    def find_evidence_sentence(self, clinical_text: str, criterion_concept: str) -> Dict[str, Any]:
        """
        Splits clinical note into sentences, lexically pre-ranks candidate sentences,
        and uses BioBERT NLI on the top candidate to verify semantic entailment/contradiction.
        """
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clinical_text) if len(s.strip()) > 5]
        if not sentences:
            sentences = [clinical_text]

        # Extract meaningful concept keywords
        stopwords = {"patient", "has", "the", "and", "with", "prior", "for", "history", "active"}
        concept_tokens = {w for w in re.findall(r'\b\w{3,}\b', criterion_concept.lower()) if w not in stopwords}

        # Score sentences by lexical overlap
        scored_sentences = []
        for s in sentences:
            s_tokens = set(re.findall(r'\b\w{3,}\b', s.lower()))
            overlap = len(concept_tokens & s_tokens)
            scored_sentences.append((overlap, s))

        # Sort descending by overlap
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        top_candidates = [s for _, s in scored_sentences[:2]] if scored_sentences else [sentences[0]]

        best_sentence = top_candidates[0]
        best_eval = None
        max_relevance = -1.0

        for sentence in top_candidates:
            res = self.evaluate_pair(premise=sentence, hypothesis=criterion_concept)
            relevance = res["probabilities"]["entailment"] + res["probabilities"]["contradiction"]
            if relevance > max_relevance:
                max_relevance = relevance
                best_sentence = sentence
                best_eval = res

        if best_eval is None:
            best_eval = self.evaluate_pair(premise=best_sentence, hypothesis=criterion_concept)

        return {
            "evidence_sentence": best_sentence,
            "nli_result": best_eval
        }

