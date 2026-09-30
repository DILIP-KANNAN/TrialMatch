"""
Evidence Agent for TrialMatch 2.0.
Coordinates atomic criterion verification across tools (Numeric, BioBERT, Terminology)
and extracts exact quotation evidence from the patient record.
"""

from typing import Dict, Any, List
from tools.numeric_tool import NumericTool
from tools.terminology_tool import TerminologyTool
from tools.biobert_tool import BioBERTTool

class EvidenceAgent:
    """
    Evaluates individual atomic criteria against a patient's profile and clinical text.
    """

    def __init__(self):
        self.biobert = BioBERTTool.get_instance()

    def evaluate_criterion(
        self,
        criterion: Dict[str, Any],
        patient: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluates a single atomic criterion against a patient.
        Returns a standardized criterion evaluation dict.
        """
        crit_id = criterion.get("id", "unknown")
        clause = criterion.get("clause", "inclusion")
        crit_type = criterion.get("type", "semantic")
        desc = criterion.get("description", "")
        profile = patient.get("structured_profile", {})
        clinical_text = patient.get("clinical_text", "")

        # ----------------------------------------------------
        # 1. Numeric Criterion
        # ----------------------------------------------------
        if crit_type == "numeric":
            field = criterion.get("field", "")
            operator = criterion.get("operator", "")
            value = criterion.get("value")

            res = NumericTool.evaluate(
                field=field,
                operator=operator,
                target_value=value,
                patient_profile=profile,
                clinical_text=clinical_text
            )

            # If it's an exclusion clause, passing the numeric condition means they ARE excluded (FAIL for patient)
            status = res["status"]
            evidence = res["evidence"]
            if clause == "exclusion" and status in ("PASS", "FAIL"):
                # If they meet the exclusion criteria, they FAIL the trial
                status = "FAIL" if res["status"] == "PASS" else "PASS"
                evidence += f" (Exclusion rule triggered: patient is {'excluded' if status == 'FAIL' else 'cleared'})."

            return {
                "criterion_id": crit_id,
                "rule_description": desc,
                "clause": clause,
                "status": status,
                "evidence_quote": evidence,
                "tool_used": "numeric_tool",
                "confidence": res.get("confidence", 1.0),
                "action_required": res.get("action_required")
            }

        # ----------------------------------------------------
        # 2. Semantic & Medical Concepts (BioBERT + Terminology)
        # ----------------------------------------------------
        concept = criterion.get("concept", desc)

        # Check special case: Insulin history
        if "insulin" in concept.lower():
            ins_res = TerminologyTool.check_insulin_history(profile, clinical_text)
            has_insulin = ins_res["has_insulin"]
            evidence = ins_res["evidence"]

            if "no prior" in concept.lower() or "no history" in concept.lower() or clause == "exclusion":
                # Trial wants NO insulin
                passed = not has_insulin
            else:
                passed = has_insulin

            return {
                "criterion_id": crit_id,
                "rule_description": desc,
                "clause": clause,
                "status": "PASS" if passed else "FAIL",
                "evidence_quote": evidence,
                "tool_used": "terminology_tool",
                "confidence": ins_res["confidence"]
            }

        # Check structured contraindications and conditions first
        cleared_list = profile.get("contraindications_cleared", [])
        if clause == "exclusion":
            for cl in cleared_list:
                concept_words = [w for w in concept.lower().split() if len(w) > 4]
                if any(w in cl.lower() for w in concept_words):
                    return {
                        "criterion_id": crit_id,
                        "rule_description": desc,
                        "clause": clause,
                        "status": "PASS",
                        "evidence_quote": f"Clinical profile explicitly clears contraindication: '{cl}'.",
                        "tool_used": "terminology_tool",
                        "confidence": 1.0
                    }
            has_cond, cond_ev = TerminologyTool.patient_has_condition(profile, concept)
            if has_cond:
                return {
                    "criterion_id": crit_id,
                    "rule_description": desc,
                    "clause": clause,
                    "status": "FAIL",
                    "evidence_quote": f"Patient has confirmed exclusion diagnosis: {cond_ev}",
                    "tool_used": "terminology_tool",
                    "confidence": 1.0
                }

        # Use BioBERT sentence-level semantic inference
        nli_evidence = self.biobert.find_evidence_sentence(clinical_text, concept)
        best_sentence = nli_evidence["evidence_sentence"]
        nli_res = nli_evidence["nli_result"]
        label = nli_res["predicted_label"]
        conf = nli_res["confidence"]

        if clause == "inclusion":
            # Inclusion wants Entailment (or high similarity)
            if label == "Entailment":
                status = "PASS"
                note = f"BioBERT detected Entailment ({round(conf*100, 1)}% confidence)."
            elif label == "Contradiction":
                status = "FAIL"
                note = f"BioBERT detected Contradiction ({round(conf*100, 1)}% confidence)."
            else:
                # Neutral: check if condition is present in structured profile
                has_cond, cond_evidence = TerminologyTool.patient_has_condition(profile, concept)
                if has_cond:
                    status = "PASS"
                    note = f"Confirmed via structured medical profile: {cond_evidence}"
                else:
                    status = "UNKNOWN"
                    note = "Insufficient specific documentation in note."
        else:
            # Exclusion wants patient NOT to have condition (Contradiction or Neutral)
            if label == "Contradiction":
                status = "PASS" # Patient contradicts exclusion -> clears exclusion
                note = f"Patient contradicts exclusion criterion ({round(conf*100, 1)}% confidence)."
            elif label == "Entailment":
                status = "FAIL" # Patient entails exclusion -> violated!
                note = f"Patient entails exclusion criterion ({round(conf*100, 1)}% confidence) - Excluded."
            else:
                # Neutral - verify with structured profile
                has_cond, _ = TerminologyTool.patient_has_condition(profile, concept)
                if has_cond:
                    status = "FAIL"
                    note = f"Patient structured profile confirms exclusion condition: '{concept}'."
                else:
                    status = "PASS"
                    note = "No evidence of exclusion condition found in clinical narrative."

        evidence_quote = f"\"{best_sentence}\" — [{note}]"

        return {
            "criterion_id": crit_id,
            "rule_description": desc,
            "clause": clause,
            "status": status,
            "evidence_quote": evidence_quote,
            "tool_used": "biobert_tool",
            "confidence": conf
        }

    def evaluate_all_criteria(
        self,
        trial: Dict[str, Any],
        patient: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Evaluates all atomic criteria for a patient-trial pair."""
        criteria = trial.get("criteria", [])
        results = []
        for crit in criteria:
            ev = self.evaluate_criterion(crit, patient)
            results.append(ev)
        return results
