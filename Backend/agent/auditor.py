"""
Clinical Auditor Agent for TrialMatch 2.0.
Performs verification, detects data gaps (missing labs/assessments), flags safety contradictions,
and assigns overall match tier: HIGH, NEEDS VERIFICATION, or NOT SUITABLE.
"""

from typing import List, Dict, Any
from agent.state import MatchTier, CriterionEvaluation

class ClinicalAuditor:
    """
    Audits the set of atomic criterion evaluations for a candidate patient-trial pair.
    """

    @classmethod
    def audit_match(
        cls,
        patient_id: str,
        trial_id: str,
        evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Takes raw criterion evaluations and produces an audited match verdict:
        - HIGH: All inclusions PASS, all exclusions PASS, 0 UNKNOWN, 0 FAIL.
        - NEEDS VERIFICATION: All evaluated criteria PASS, but 1 or more criteria are UNKNOWN (e.g. missing lab).
        - NOT SUITABLE: 1 or more inclusions FAIL or 1 or more exclusions FAIL (i.e. violated).
        """
        passed_count = 0
        failed_count = 0
        unknown_count = 0
        total = len(evaluations)

        action_items: List[str] = []
        critical_violations: List[str] = []

        for ev in evaluations:
            status = ev.get("status")
            clause = ev.get("clause")
            rule = ev.get("rule_description", "")
            action = ev.get("action_required")

            if status == "FAIL":
                failed_count += 1
                critical_violations.append(f"Violated {clause.upper()} criterion: '{rule}'")
            elif status == "UNKNOWN":
                unknown_count += 1
                if action:
                    action_items.append(action)
                else:
                    action_items.append(f"Verify status for: '{rule}'")
            elif status == "PASS":
                passed_count += 1

        # Determine Tier
        if failed_count > 0:
            tier: MatchTier = "NOT SUITABLE"
            # Score reflects proportion passed, heavily penalized for hard failures
            base_score = (passed_count / max(total, 1)) * 50.0
            score = round(base_score, 1)
            summary = (
                f"Candidate excluded due to {failed_count} unmet/violated criterion(a). "
                f"Primary reason: {critical_violations[0] if critical_violations else 'Criteria failure.'}"
            )
        elif unknown_count > 0:
            tier = "NEEDS VERIFICATION"
            # Inclusions passed so far, but needs verification
            score = round(70.0 + (passed_count / max(total, 1)) * 20.0 - (unknown_count * 5.0), 1)
            summary = (
                f"Strong candidate meeting all verified criteria, but requires clinical/laboratory "
                f"verification for {unknown_count} unrecorded metric(s)."
            )
        else:
            tier = "HIGH"
            score = round(90.0 + (passed_count / max(total, 1)) * 10.0, 1)
            summary = f"High-confidence match! Patient satisfies all {passed_count} inclusion and exclusion criteria with verified evidence."

        return {
            "tier": tier,
            "match_score": min(100.0, max(0.0, score)),
            "summary": summary,
            "counts": {
                "total": total,
                "passed": passed_count,
                "failed": failed_count,
                "unknown": unknown_count
            },
            "action_items": list(dict.fromkeys(action_items)), # unique preserved order
            "critical_violations": critical_violations
        }
