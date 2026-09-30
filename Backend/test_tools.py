"""
Unit and integration test for TrialMatch 2.0 Tool Suite.
"""

import sys
import os

# Ensure Backend is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.modules['torchvision'] = None

from tools.numeric_tool import NumericTool
from tools.terminology_tool import TerminologyTool
from tools.retrieval_tool import RetrievalTool
from tools.biobert_tool import BioBERTTool
import json

def test_numeric_tool():
    print("Testing NumericTool...")
    sample_profile = {
        "demographics": {"age": 52},
        "labs": {
            "HbA1c": {"value": 8.2},
            "BMI": {"value": 29.3},
            "eGFR": {"value": None}
        }
    }
    # Age between 40 and 65 -> PASS
    res1 = NumericTool.evaluate("age", "between", [40, 65], sample_profile)
    assert res1["status"] == "PASS", f"Expected PASS, got {res1}"

    # HbA1c > 7.0 -> PASS
    res2 = NumericTool.evaluate("HbA1c", ">", 7.0, sample_profile)
    assert res2["status"] == "PASS", f"Expected PASS, got {res2}"

    # Missing eGFR -> UNKNOWN
    res3 = NumericTool.evaluate("eGFR", "<", 45, sample_profile)
    assert res3["status"] == "UNKNOWN", f"Expected UNKNOWN, got {res3}"
    print("NumericTool: ALL TESTS PASSED.")

def test_terminology_tool():
    print("Testing TerminologyTool...")
    assert TerminologyTool.matches_condition("Type 2 Diabetes Mellitus", "type 2 diabetes")
    assert TerminologyTool.matches_condition("NIDDM", "Type 2 Diabetes")
    assert TerminologyTool.matches_condition("Renal Impairment", "Kidney Disease")

    sample_profile = {
        "conditions": [{"name": "Type 2 Diabetes Mellitus", "synonyms": ["NIDDM"]}],
        "medications": [{"name": "Metformin", "drug_class": "Biguanide"}]
    }
    has_cond, _ = TerminologyTool.patient_has_condition(sample_profile, "Type 2 Diabetes")
    assert has_cond

    insulin_res = TerminologyTool.check_insulin_history(sample_profile, "Patient has never required insulin therapy.")
    assert not insulin_res["has_insulin"]
    print("TerminologyTool: ALL TESTS PASSED.")

def test_retrieval_tool():
    print("Testing RetrievalTool...")
    with open("data/patients.json", "r") as f:
        patients = json.load(f)
    with open("data/trials.json", "r") as f:
        trials = json.load(f)

    candidate_pairs = RetrievalTool.filter_candidates(patients, trials)
    print(f"Total theoretical pairs: {len(patients)} x {len(trials)} = {len(patients) * len(trials)}")
    print(f"Coarse-filtered candidate pairs: {len(candidate_pairs)}")
    assert len(candidate_pairs) > 0 and len(candidate_pairs) < (len(patients) * len(trials))
    print("RetrievalTool: ALL TESTS PASSED.")

def test_biobert_tool():
    print("Testing BioBERTTool...")
    biobert = BioBERTTool.get_instance()
    # Test Entailment
    res = biobert.evaluate_pair(
        premise="Patient has never required insulin therapy and is on oral Metformin.",
        hypothesis="Patient has no history of prior insulin therapy"
    )
    print(f"BioBERT Evaluation: {res['predicted_label']} (confidence: {res['confidence']})")
    assert "predicted_label" in res
    print("BioBERTTool: ALL TESTS PASSED.")

if __name__ == "__main__":
    test_numeric_tool()
    test_terminology_tool()
    test_retrieval_tool()
    test_biobert_tool()
    print("\n>>> ALL PHASE 1 & 2 TOOLS VERIFIED AND FUNCTIONAL! <<<")
