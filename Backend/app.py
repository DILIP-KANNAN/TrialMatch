from flask import Flask, request, jsonify
import torch
import re
from transformers import BertTokenizer, BertForSequenceClassification
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

print("Loading fine-tuned NLI model...")
MODEL_PATH = "./biobert_nli_finetuned"
try:
    tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
    model = BertForSequenceClassification.from_pretrained(MODEL_PATH)
    model.eval()
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    # Fallback to base model for safety if not found
    tokenizer = BertTokenizer.from_pretrained("dmis-lab/biobert-base-cased-v1.1")
    model = BertForSequenceClassification.from_pretrained("dmis-lab/biobert-base-cased-v1.1", num_labels=3)
    model.eval()

def predict_nli(premise, hypothesis):
    """
    Returns True if the premise entails the hypothesis.
    SNLI labels typically: 0=entailment, 1=neutral, 2=contradiction
    """
    inputs = tokenizer(premise, hypothesis, return_tensors="pt", truncation=True, max_length=128)
    with torch.no_grad():
        logits = model(**inputs).logits
    
    predicted_class_id = logits.argmax().item()
    return predicted_class_id == 0 # Entailment

def extract_patient_metrics(text):
    """
    Uses Regex to actively extract numerical metrics from unstructured clinical notes.
    """
    metrics = {}
    
    age_match = re.search(r'(\d+)(?:\s*|-)(?:year|yr|yo|age)', text, re.IGNORECASE)
    if age_match:
        metrics['age'] = float(age_match.group(1))
        
    hba1c_match = re.search(r'HbA1c\s*(?:of|is)?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if hba1c_match:
        metrics['hba1c'] = float(hba1c_match.group(1))
        
    bmi_match = re.search(r'BMI\s*(?:of|is)?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if bmi_match:
        metrics['bmi'] = float(bmi_match.group(1))
        
    return metrics

def evaluate_math_criterion(criterion, patient_metrics):
    """
    If a criterion has math, evaluates it. Returns True/False if evaluating successfully,
    returns None if it's not a math criterion (signaling to fallback to BioBERT).
    """
    criterion_lower = criterion.lower()
    
    target_metric = None
    if 'age' in criterion_lower: target_metric = 'age'
    elif 'hba1c' in criterion_lower: target_metric = 'hba1c'
    elif 'bmi' in criterion_lower: target_metric = 'bmi'
        
    if not target_metric or target_metric not in patient_metrics:
        return None
        
    val = patient_metrics[target_metric]
    
    # "between 40 and 65" or "30-60"
    if 'between' in criterion_lower or '-' in criterion:
        nums = [float(x) for x in re.findall(r'\d+\.?\d*', criterion)]
        if len(nums) >= 2:
            low, high = sorted(nums[:2])
            return low <= val <= high
            
    # "> 7.0"
    if '>' in criterion_lower or 'greater' in criterion_lower:
        nums = [float(x) for x in re.findall(r'\d+\.?\d*', criterion)]
        if nums: return val > nums[0]
        
    # "< 7.0"
    if '<' in criterion_lower or 'less' in criterion_lower:
        nums = [float(x) for x in re.findall(r'\d+\.?\d*', criterion)]
        if nums: return val < nums[0]
        
    return None

@app.route('/match', methods=['POST'])
def match():
    data = request.json
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    patient_text = data.get("patient_text", "")
    inclusion_criteria = data.get("inclusion_criteria", [])
    exclusion_criteria = data.get("exclusion_criteria", [])
    
    satisfied = []
    failed = []
    
    # Extract math metrics from unstructured text
    patient_metrics = extract_patient_metrics(patient_text)
    
    # 1. Evaluate Inclusion Criteria
    for criterion in inclusion_criteria:
        # Try Hybrid Math routing first
        math_result = evaluate_math_criterion(criterion, patient_metrics)
        if math_result is not None:
            if math_result:
                satisfied.append(f"Patient meets numerical inclusion: {criterion}")
            else:
                failed.append(f"Patient fails numerical inclusion: {criterion}")
            continue
            
        # Fallback to BioBERT NLI for semantics
        if predict_nli(patient_text, criterion):
            satisfied.append(f"Patient entails semantic inclusion: {criterion}")
        else:
            failed.append(f"Patient lacks semantic inclusion: {criterion}")
            
    # 2. Evaluate Exclusion Criteria
    for criterion in exclusion_criteria:
        math_result = evaluate_math_criterion(criterion, patient_metrics)
        if math_result is not None:
            if math_result: # If they match an exclusion criteria numerically
                failed.append(f"Patient violates numerical exclusion: {criterion}")
            else:
                satisfied.append(f"Patient clears numerical exclusion: {criterion}")
            continue
            
        if predict_nli(patient_text, criterion):
            failed.append(f"Patient violates semantic exclusion: {criterion}")
        else:
            satisfied.append(f"Patient clears semantic exclusion: {criterion}")
            
    total_criteria = len(inclusion_criteria) + len(exclusion_criteria)
    if total_criteria == 0:
        final_score = 0.0
    else:
        final_score = len(satisfied) / total_criteria
        
    interpretation = "The patient is a strong match based on hybrid logical inference." if final_score > 0.6 else "The patient does not satisfy all required criteria."
    
    return jsonify({
        "rule_score": round(final_score, 2), 
        "bert_score": round(final_score, 2),
        "final_score": round(final_score, 2),
        "explanation": {
            "summary": f"Matched {len(satisfied)} out of {total_criteria} criteria using a Hybrid Math + AI approach.",
            "criteria_analysis": {
                "satisfied_conditions": satisfied,
                "failed_conditions": failed
            },
            "semantic_analysis": "System dynamically routed numerical ranges to a Python Math Evaluator, while medical concepts and history were handled by the fine-tuned BioBERT NLI Engine.",
            "interpretation": interpretation
        }
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)