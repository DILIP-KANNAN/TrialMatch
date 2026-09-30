"""
Matchmaker Orchestrator for TrialMatch 2.0.
Goal-driven central brain: autonomously coordinates Population Discovery,
Coarse-to-Fine Retrieval, Deep NLP Evidence Verification, and Clinical Auditing.
"""

import json
import os
from typing import Dict, Any, List, Optional, Callable
from agent.auditor import ClinicalAuditor
from agents.evidence_agent import EvidenceAgent
from tools.retrieval_tool import RetrievalTool

class MatchmakerOrchestrator:
    """
    Central Brain / Orchestrator Agent.
    Executes the goal:
    'Find all potentially suitable patients for the available trials and provide evidence for each match.'
    """

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(backend_dir, "data")
        self.data_dir = data_dir
        self.evidence_agent = EvidenceAgent()

    def load_fleet_data(self) -> tuple:
        """Loads patients.json and trials.json from data directory."""
        pts_path = os.path.join(self.data_dir, "patients.json")
        trials_path = os.path.join(self.data_dir, "trials.json")

        with open(pts_path, "r", encoding="utf-8") as f:
            patients = json.load(f)
        with open(trials_path, "r", encoding="utf-8") as f:
            trials = json.load(f)

        return patients, trials

    def run_matchmaking_fleet(
        self,
        log_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Executes the full agentic loop across the entire population:
        1. Ingest fleet data
        2. Stage 1: Coarse candidate retrieval
        3. Stage 2: Deep NLP evidence verification
        4. Stage 3: Clinical safety audit & reflection
        5. Stage 4: Dual-view synthesis (trial-centric & patient-centric)
        """
        logs = []
        def emit(msg: str):
            logs.append(msg)
            if log_callback:
                log_callback(msg)
            print(f"[Matchmaker] {msg}")

        emit("Initializing Matchmaker Orchestrator fleet run...")
        patients, trials = self.load_fleet_data()
        emit(f"Loaded patient population ({len(patients)} patients) and trial registry ({len(trials)} active protocols).")

        # Stage 1: Coarse Candidate Retrieval
        emit("Running Stage 1: Coarse Demographic & Condition Retrieval Filter...")
        candidate_pairs = RetrievalTool.filter_candidates(patients, trials)
        total_possible = len(patients) * len(trials)
        emit(
            f"Candidate Retrieval Complete: Filtered {total_possible} theoretical pairs down to "
            f"{len(candidate_pairs)} plausible candidate pairs (pruned {round((1 - len(candidate_pairs)/max(total_possible,1))*100, 1)}% of search space)."
        )

        # Stage 2 & 3: Deep NLP Verification & Clinical Audit
        emit("Starting Stage 2 & 3: Deep NLP Evidence Verification and Clinical Safety Audit...")
        assessments: List[Dict[str, Any]] = []

        by_trial: Dict[str, List[Dict[str, Any]]] = {t["trial_id"]: [] for t in trials}
        by_patient: Dict[str, List[Dict[str, Any]]] = {p["patient_id"]: [] for p in patients}

        high_count = 0
        needs_verif_count = 0
        excluded_count = 0

        for i, pair in enumerate(candidate_pairs, start=1):
            p = pair["patient"]
            t = pair["trial"]
            pid = pair["patient_id"]
            tid = pair["trial_id"]

            if i % 25 == 0 or i == len(candidate_pairs):
                emit(f"Evaluating candidate pair {i}/{len(candidate_pairs)}: Patient {pid} <-> Trial {tid}...")

            # Evaluate atomic criteria
            evaluations = self.evidence_agent.evaluate_all_criteria(trial=t, patient=p)

            # Audit evaluations
            audit = ClinicalAuditor.audit_match(patient_id=pid, trial_id=tid, evaluations=evaluations)

            tier = audit["tier"]
            if tier == "HIGH":
                high_count += 1
            elif tier == "NEEDS VERIFICATION":
                needs_verif_count += 1
            else:
                excluded_count += 1

            assessment_record = {
                "match_id": f"M_{pid}_{tid}",
                "patient_id": pid,
                "patient_name": p.get("name", ""),
                "trial_id": tid,
                "trial_name": t.get("name", ""),
                "tier": tier,
                "match_score": audit["match_score"],
                "summary": audit["summary"],
                "counts": audit["counts"],
                "action_items": audit["action_items"],
                "critical_violations": audit["critical_violations"],
                "criteria_evaluations": evaluations
            }

            assessments.append(assessment_record)
            by_trial[tid].append(assessment_record)
            by_patient[pid].append(assessment_record)

        # Sort candidate lists by score descending
        for tid in by_trial:
            by_trial[tid].sort(key=lambda x: x["match_score"], reverse=True)

        for pid in by_patient:
            by_patient[pid].sort(key=lambda x: x["match_score"], reverse=True)

        emit(
            f"Fleet Matchmaking Complete: Generated {len(assessments)} verified assessments across {len(patients)} patients. "
            f"Summary: {high_count} HIGH Matches, {needs_verif_count} NEEDS VERIFICATION, {excluded_count} EXCLUDED/NOT SUITABLE."
        )

        return {
            "total_patients": len(patients),
            "total_trials": len(trials),
            "total_evaluated_pairs": len(assessments),
            "high_match_count": high_count,
            "verification_needed_count": needs_verif_count,
            "excluded_count": excluded_count,
            "by_trial": by_trial,
            "by_patient": by_patient,
            "execution_logs": logs
        }
