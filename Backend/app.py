import os
import sys

# Ensure backend root is in Python path and prevent torchvision import collision
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.modules['torchvision'] = None

from flask import Flask, request, jsonify
from flask_cors import CORS
import json

from agent.orchestrator import MatchmakerOrchestrator
from tools.biobert_tool import BioBERTTool
from tools.numeric_tool import NumericTool

app = Flask(__name__)
CORS(app)

print("[Backend] Initializing TrialMatch 2.0 Engine...")
orchestrator = MatchmakerOrchestrator()
cached_fleet_results = None

# Pre-run or load data
try:
    patients, trials = orchestrator.load_fleet_data()
    print(f"[Backend] Successfully loaded {len(patients)} patients and {len(trials)} trials.")
except Exception as e:
    print(f"[Backend] Error loading initial fleet data: {e}")
    patients, trials = [], []


@app.route('/api/fleet/status', methods=['GET'])
def get_fleet_status():
    """Returns current fleet matching cache status."""
    global cached_fleet_results
    return jsonify({
        "status": "ready" if cached_fleet_results is not None else "idle",
        "has_cached_results": cached_fleet_results is not None,
        "total_patients": len(patients),
        "total_trials": len(trials),
        "summary": {
            "high_matches": cached_fleet_results.get("high_match_count", 0) if cached_fleet_results else 0,
            "needs_verification": cached_fleet_results.get("verification_needed_count", 0) if cached_fleet_results else 0,
            "excluded": cached_fleet_results.get("excluded_count", 0) if cached_fleet_results else 0,
            "total_evaluated_pairs": cached_fleet_results.get("total_evaluated_pairs", 0) if cached_fleet_results else 0
        }
    })


@app.route('/api/fleet/run', methods=['POST'])
def run_fleet_match():
    """Triggers the full Matchmaker Orchestrator across the patient and trial populations."""
    global cached_fleet_results
    try:
        print("[Backend] Executing Matchmaker Orchestrator fleet run...")
        cached_fleet_results = orchestrator.run_matchmaking_fleet()
        return jsonify({
            "success": True,
            "message": "Fleet matchmaking completed successfully.",
            "data": cached_fleet_results
        })
    except Exception as e:
        print(f"[Backend] Error running fleet matchmaker: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/fleet/results', methods=['GET'])
def get_fleet_results():
    """Returns the cached fleet matchmaking results (or runs on-demand if not yet computed)."""
    global cached_fleet_results
    if cached_fleet_results is None:
        print("[Backend] No cached results found. Running initial fleet matchmaking...")
        cached_fleet_results = orchestrator.run_matchmaking_fleet()
    return jsonify(cached_fleet_results)


@app.route('/api/fleet/trials', methods=['GET'])
def get_trials():
    """Returns all active clinical trial protocols with decomposed atomic criteria."""
    return jsonify(trials)


@app.route('/api/fleet/patients', methods=['GET'])
def get_patients():
    """Returns all hospital patient records with structured profiles."""
    return jsonify(patients)


@app.route('/api/fleet/matches/by-trial/<trial_id>', methods=['GET'])
def get_matches_by_trial(trial_id):
    """Returns candidates for a specific trial, ranked by score."""
    global cached_fleet_results
    if cached_fleet_results is None:
        cached_fleet_results = orchestrator.run_matchmaking_fleet()
    matches = cached_fleet_results.get("by_trial", {}).get(trial_id, [])
    return jsonify({"trial_id": trial_id, "candidates": matches})


@app.route('/api/fleet/matches/by-patient/<patient_id>', methods=['GET'])
def get_matches_by_patient(patient_id):
    """Returns trial opportunities for a specific patient, ranked by score."""
    global cached_fleet_results
    if cached_fleet_results is None:
        cached_fleet_results = orchestrator.run_matchmaking_fleet()
    matches = cached_fleet_results.get("by_patient", {}).get(patient_id, [])
    return jsonify({"patient_id": patient_id, "trials": matches})


# ==========================================
# Legacy Single Pair Match Endpoint
# ==========================================
@app.route('/match', methods=['POST'])
def legacy_match():
    """Legacy backward-compatible single match endpoint."""
    data = request.json
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    patient_text = data.get("patient_text", "")
    inclusion_criteria = data.get("inclusion_criteria", [])
    exclusion_criteria = data.get("exclusion_criteria", [])

    biobert = BioBERTTool.get_instance()
    satisfied = []
    failed = []

    # Simple numeric regex
    patient_metrics = {}
    import re
    age_match = re.search(r'(\d+)(?:\s*|-)(?:year|yr|yo|age)', patient_text, re.IGNORECASE)
    if age_match: patient_metrics['age'] = float(age_match.group(1))
    hba1c_match = re.search(r'HbA1c\s*(?:of|is)?\s*(\d+\.?\d*)', patient_text, re.IGNORECASE)
    if hba1c_match: patient_metrics['hba1c'] = float(hba1c_match.group(1))
    bmi_match = re.search(r'BMI\s*(?:of|is)?\s*(\d+\.?\d*)', patient_text, re.IGNORECASE)
    if bmi_match: patient_metrics['bmi'] = float(bmi_match.group(1))

    # Evaluate inclusion
    for criterion in inclusion_criteria:
        nli_res = biobert.evaluate_pair(patient_text, criterion)
        if nli_res["is_entailment"]:
            satisfied.append(f"Entails: {criterion}")
        else:
            failed.append(f"Fails: {criterion}")

    # Evaluate exclusion
    for criterion in exclusion_criteria:
        nli_res = biobert.evaluate_pair(patient_text, criterion)
        if nli_res["is_contradiction"] or nli_res["predicted_label"] == "Neutral":
            satisfied.append(f"Clears exclusion: {criterion}")
        else:
            failed.append(f"Violates exclusion: {criterion}")

    total = len(inclusion_criteria) + len(exclusion_criteria)
    final_score = len(satisfied) / max(total, 1)

    return jsonify({
        "rule_score": round(final_score, 2),
        "bert_score": round(final_score, 2),
        "final_score": round(final_score, 2),
        "explanation": {
            "summary": f"Matched {len(satisfied)} out of {total} criteria.",
            "criteria_analysis": {
                "satisfied_conditions": satisfied,
                "failed_conditions": failed
            },
            "semantic_analysis": "Evaluated using fine-tuned BioBERT NLI engine.",
            "interpretation": "Eligible" if final_score > 0.6 else "Not Eligible"
        }
    })


if __name__ == '__main__':
    # Pre-cache fleet results on boot
    print("[Backend] Pre-caching fleet matchmaking results...")
    cached_fleet_results = orchestrator.run_matchmaking_fleet()
    print("[Backend] Server ready on http://127.0.0.1:5000")
    app.run(port=5000, debug=False)