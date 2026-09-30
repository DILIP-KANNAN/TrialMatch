"""
Stage 1 Coarse Retrieval Tool for TrialMatch 2.0.
Inexpensively prunes the Patient Population x Trial Population space down to plausible candidate pairs.
Implements multi-stage coarse filtering:
1. Condition matching
2. Age bracket filtering
3. Known labs rough filters (HbA1c, BMI, eGFR)
4. Primary contraindication screening (e.g. insulin history)
"""

from typing import List, Dict, Any, Optional
from tools.terminology_tool import TerminologyTool
from tools.numeric_tool import NumericTool

class RetrievalTool:
    """
    Performs fast, low-compute filtering:
    Prunes the N patients x M trials search space down to high-relevance candidates for deep NLP verification.
    """

    @classmethod
    def filter_candidates(
        cls,
        patients: List[Dict[str, Any]],
        trials: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Takes N patients and M trials, returns filtered candidate pairs.
        """
        candidate_pairs = []

        for trial in trials:
            target_cond = trial.get("target_condition", "")
            criteria = trial.get("criteria", [])

            # Pre-parse numeric constraints from trial criteria
            numeric_inclusions = [c for c in criteria if c.get("type") == "numeric" and c.get("clause") == "inclusion"]
            has_insulin_exclusion = any(
                "insulin" in c.get("concept", "").lower() and c.get("clause") == "exclusion"
                for c in criteria
            )
            requires_no_insulin = any(
                "no prior insulin" in c.get("concept", "").lower() and c.get("clause") == "inclusion"
                for c in criteria
            ) or has_insulin_exclusion

            for patient in patients:
                profile = patient.get("structured_profile", {})
                clinical_text = patient.get("clinical_text", "")

                # ----------------------------------------------------
                # Filter 1: Primary Condition Match
                # ----------------------------------------------------
                cond_match, _ = TerminologyTool.patient_has_condition(profile, target_cond)
                if not cond_match and target_cond.lower() not in clinical_text.lower():
                    continue

                # ----------------------------------------------------
                # Filter 2: Numeric Inclusion Coarse Check
                # ----------------------------------------------------
                skip_candidate = False
                for crit in numeric_inclusions:
                    field = crit.get("field", "")
                    op = crit.get("operator", "")
                    val = crit.get("value")

                    # If patient has this lab/demographic, evaluate it
                    eval_res = NumericTool.evaluate(
                        field=field,
                        operator=op,
                        target_value=val,
                        patient_profile=profile,
                        clinical_text="" # strict profile check for fast pruning
                    )
                    # If patient explicitly has the value and FAILS inclusion, prune them!
                    if eval_res["status"] == "FAIL":
                        skip_candidate = True
                        break

                if skip_candidate:
                    continue

                # ----------------------------------------------------
                # Filter 3: Primary Exclusion Pre-Screen (Insulin)
                # ----------------------------------------------------
                if requires_no_insulin:
                    ins_info = TerminologyTool.check_insulin_history(profile, clinical_text)
                    if ins_info["has_insulin"]:
                        # Trial forbids insulin, but patient is on insulin -> prune!
                        continue

                # Candidate passed all coarse filters!
                candidate_pairs.append({
                    "patient_id": patient.get("patient_id"),
                    "trial_id": trial.get("trial_id"),
                    "patient": patient,
                    "trial": trial,
                    "condition_matched": target_cond
                })

        return candidate_pairs
