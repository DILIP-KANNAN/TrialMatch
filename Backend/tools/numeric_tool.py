"""
Numeric & Lab Evaluation Tool for TrialMatch 2.0.
Performs deterministic interval and relational arithmetic for clinical criteria.
"""

from typing import Dict, Any, Optional, Union, List, Tuple
import re

class NumericTool:
    """
    Evaluates quantitative criteria (e.g. age, HbA1c, BMI, eGFR, systolic/diastolic BP).
    Handles exact values from structured profile and falls back to regex extraction from raw text.
    """

    @staticmethod
    def extract_from_text(field_name: str, clinical_text: str) -> Optional[float]:
        """Dynamically attempts regex extraction of numbers from clinical text if not in profile."""
        field_lower = field_name.lower()
        if "age" in field_lower:
            m = re.search(r'(\d{1,3})(?:\s*|-)(?:year|yr|yo|age)', clinical_text, re.IGNORECASE)
            if m:
                return float(m.group(1))
        elif "hba1c" in field_lower or "a1c" in field_lower:
            m = re.search(r'(?:hba1c|a1c)\s*(?:of|is|:)?\s*(\d+\.?\d*)', clinical_text, re.IGNORECASE)
            if m:
                return float(m.group(1))
        elif "bmi" in field_lower:
            m = re.search(r'bmi\s*(?:of|is|:)?\s*(\d+\.?\d*)', clinical_text, re.IGNORECASE)
            if m:
                return float(m.group(1))
        elif "egfr" in field_lower:
            m = re.search(r'egfr\s*(?:of|is|:)?\s*(\d+\.?\d*)', clinical_text, re.IGNORECASE)
            if m:
                return float(m.group(1))
        return None

    @classmethod
    def evaluate(
        cls,
        field: str,
        operator: str,
        target_value: Union[float, List[float]],
        patient_profile: Dict[str, Any],
        clinical_text: str = ""
    ) -> Dict[str, Any]:
        """
        Evaluates a numeric criterion.
        Returns:
            {
                "status": "PASS" | "FAIL" | "UNKNOWN",
                "patient_value": float or None,
                "evidence": str,
                "confidence": float
            }
        """
        # 1. Resolve patient value
        patient_val: Optional[float] = None
        source = "structured_profile"

        # Check demographics
        if field.lower() == "age":
            demo = patient_profile.get("demographics", {})
            patient_val = demo.get("age")
        else:
            # Check labs
            labs = patient_profile.get("labs", {})
            for lab_key, lab_data in labs.items():
                if lab_key.lower() == field.lower():
                    if isinstance(lab_data, dict):
                        patient_val = lab_data.get("value")
                    elif isinstance(lab_data, (int, float)):
                        patient_val = float(lab_data)
                    break

        # Fallback to regex in clinical text
        if patient_val is None and clinical_text:
            extracted = cls.extract_from_text(field, clinical_text)
            if extracted is not None:
                patient_val = extracted
                source = "extracted_from_clinical_text"

        # If still unknown
        if patient_val is None:
            return {
                "status": "UNKNOWN",
                "patient_value": None,
                "evidence": f"Patient profile and clinical text have no recorded value for '{field}'.",
                "confidence": 0.0,
                "action_required": f"Obtain laboratory test or documentation for {field}."
            }

        # 2. Evaluate operator
        op = operator.lower().strip()
        passed = False

        if op in ("between", "range") and isinstance(target_value, (list, tuple)) and len(target_value) >= 2:
            low, high = sorted([float(target_value[0]), float(target_value[1])])
            passed = (low <= patient_val <= high)
            rule_str = f"between {low} and {high}"
        elif op in (">", "gt", "greater"):
            threshold = float(target_value if not isinstance(target_value, list) else target_value[0])
            passed = (patient_val > threshold)
            rule_str = f"> {threshold}"
        elif op in (">=", "gte", "greater_equal"):
            threshold = float(target_value if not isinstance(target_value, list) else target_value[0])
            passed = (patient_val >= threshold)
            rule_str = f">= {threshold}"
        elif op in ("<", "lt", "less"):
            threshold = float(target_value if not isinstance(target_value, list) else target_value[0])
            passed = (patient_val < threshold)
            rule_str = f"< {threshold}"
        elif op in ("<=", "lte", "less_equal"):
            threshold = float(target_value if not isinstance(target_value, list) else target_value[0])
            passed = (patient_val <= threshold)
            rule_str = f"<= {threshold}"
        elif op in ("==", "=", "eq", "equal"):
            threshold = float(target_value if not isinstance(target_value, list) else target_value[0])
            passed = (patient_val == threshold)
            rule_str = f"== {threshold}"
        elif op in ("!=", "neq", "not_equal"):
            threshold = float(target_value if not isinstance(target_value, list) else target_value[0])
            passed = (patient_val != threshold)
            rule_str = f"!= {threshold}"
        else:
            return {
                "status": "UNKNOWN",
                "patient_value": patient_val,
                "evidence": f"Unsupported numeric operator '{operator}'.",
                "confidence": 0.5
            }

        status = "PASS" if passed else "FAIL"
        evidence = (
            f"Patient {field} is {patient_val} ({source}), which "
            f"{'satisfies' if passed else 'fails'} condition ({rule_str})."
        )

        return {
            "status": status,
            "patient_value": patient_val,
            "evidence": evidence,
            "confidence": 1.0
        }
