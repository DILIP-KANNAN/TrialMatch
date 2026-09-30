"""
Medical Terminology & Drug Ontology Tool for TrialMatch 2.0.
Maps medical synonyms, abbreviations (NIDDM <-> Type 2 Diabetes), and drug classes.
"""

from typing import Dict, Any, List, Optional, Set, Tuple

# Medical Synonym Mapping
CONDITION_SYNONYMS: Dict[str, Set[str]] = {
    "type 2 diabetes": {
        "type 2 diabetes", "type 2 diabetes mellitus", "t2d", "t2dm", "niddm",
        "non-insulin dependent diabetes", "adult-onset diabetes", "diabetes mellitus type 2"
    },
    "type 1 diabetes": {
        "type 1 diabetes", "type 1 diabetes mellitus", "t1d", "t1dm", "iddm",
        "insulin dependent diabetes", "juvenile diabetes"
    },
    "hypertension": {
        "hypertension", "htn", "high blood pressure", "elevated bp", "essential hypertension"
    },
    "kidney disease": {
        "kidney disease", "chronic kidney disease", "ckd", "renal impairment",
        "renal insufficiency", "nephropathy", "renal disease", "end stage renal disease", "esrd"
    },
    "heart failure": {
        "heart failure", "congestive heart failure", "chf", "cardiac failure",
        "reduced ejection fraction", "hfpef", "hfref"
    },
    "cardiovascular disease": {
        "cardiovascular disease", "cvd", "coronary artery disease", "cad",
        "myocardial infarction", "mi", "heart attack", "stroke", "cva", "transient ischemic attack", "tia"
    },
    "liver disease": {
        "liver disease", "hepatic impairment", "cirrhosis", "hepatitis", "fatty liver", "nafld", "nash"
    },
    "diabetic retinopathy": {
        "diabetic retinopathy", "retinopathy", "macular edema", "diabetic eye disease"
    },
    "diabetic neuropathy": {
        "diabetic neuropathy", "peripheral neuropathy", "diabetic nerve pain", "neuropathy"
    }
}

# Medication & Drug Class Ontology
DRUG_ONTOLOGY: Dict[str, Dict[str, Any]] = {
    "metformin": {"class": "Biguanide", "is_insulin": False},
    "glucophage": {"class": "Biguanide", "is_insulin": False},
    "glipizide": {"class": "Sulfonylurea", "is_insulin": False},
    "glimepiride": {"class": "Sulfonylurea", "is_insulin": False},
    "glyburide": {"class": "Sulfonylurea", "is_insulin": False},
    "sitagliptin": {"class": "DPP-4 Inhibitor", "is_insulin": False},
    "januvia": {"class": "DPP-4 Inhibitor", "is_insulin": False},
    "empagliflozin": {"class": "SGLT2 Inhibitor", "is_insulin": False},
    "jardiance": {"class": "SGLT2 Inhibitor", "is_insulin": False},
    "dapagliflozin": {"class": "SGLT2 Inhibitor", "is_insulin": False},
    "farxiga": {"class": "SGLT2 Inhibitor", "is_insulin": False},
    "semaglutide": {"class": "GLP-1 Receptor Agonist", "is_insulin": False},
    "ozempic": {"class": "GLP-1 Receptor Agonist", "is_insulin": False},
    "rybelsus": {"class": "GLP-1 Receptor Agonist", "is_insulin": False},
    "liraglutide": {"class": "GLP-1 Receptor Agonist", "is_insulin": False},
    "victoza": {"class": "GLP-1 Receptor Agonist", "is_insulin": False},
    "insulin glargine": {"class": "Long-Acting Insulin", "is_insulin": True},
    "lantus": {"class": "Long-Acting Insulin", "is_insulin": True},
    "basaglar": {"class": "Long-Acting Insulin", "is_insulin": True},
    "insulin lispro": {"class": "Rapid-Acting Insulin", "is_insulin": True},
    "humalog": {"class": "Rapid-Acting Insulin", "is_insulin": True},
    "insulin aspart": {"class": "Rapid-Acting Insulin", "is_insulin": True},
    "novolog": {"class": "Rapid-Acting Insulin", "is_insulin": True},
    "lisinopril": {"class": "ACE Inhibitor", "is_insulin": False},
    "losartan": {"class": "ARB", "is_insulin": False},
    "amlodipine": {"class": "Calcium Channel Blocker", "is_insulin": False},
    "atorvastatin": {"class": "Statin", "is_insulin": False},
    "lipitor": {"class": "Statin", "is_insulin": False},
}


class TerminologyTool:
    """Tool for normalizing medical entities, disease synonyms, and pharmaceutical classifications."""

    @classmethod
    def matches_condition(cls, patient_condition: str, target_condition: str) -> bool:
        """Checks whether patient condition matches target condition considering medical synonyms."""
        p_clean = patient_condition.strip().lower()
        t_clean = target_condition.strip().lower()

        if p_clean == t_clean or t_clean in p_clean or p_clean in t_clean:
            return True

        for canon, syns in CONDITION_SYNONYMS.items():
            t_in_syns = (t_clean == canon or t_clean in syns)
            p_in_syns = (p_clean == canon or p_clean in syns or any(s in p_clean for s in syns))
            if t_in_syns and p_in_syns:
                return True

        return False

    @classmethod
    def patient_has_condition(cls, patient_profile: Dict[str, Any], target_condition: str) -> Tuple[bool, str]:
        """Inspects patient conditions list and clinical text for target condition."""
        conditions = patient_profile.get("conditions", [])
        for c in conditions:
            c_name = c.get("name", "") if isinstance(c, dict) else str(c)
            if cls.matches_condition(c_name, target_condition):
                return True, f"Patient is diagnosed with '{c_name}', which matches '{target_condition}'."

        return False, f"Condition '{target_condition}' not found in patient diagnosis profile."

    @classmethod
    def check_insulin_history(cls, patient_profile: Dict[str, Any], clinical_text: str = "") -> Dict[str, Any]:
        """
        Determines if patient has history of insulin use via medication list and text.
        """
        meds = patient_profile.get("medications", [])
        for m in meds:
            m_name = m.get("name", "") if isinstance(m, dict) else str(m)
            m_clean = m_name.lower().strip()
            
            # Check ontology
            info = DRUG_ONTOLOGY.get(m_clean)
            if info and info.get("is_insulin"):
                return {
                    "has_insulin": True,
                    "evidence": f"Patient is prescribed {m_name} (Class: {info.get('class')}).",
                    "confidence": 1.0
                }
            if "insulin" in m_clean:
                return {
                    "has_insulin": True,
                    "evidence": f"Patient medication list includes '{m_name}'.",
                    "confidence": 1.0
                }

        # Check contraindications / cleared flags
        cleared = patient_profile.get("contraindications_cleared", [])
        for cl in cleared:
            if "insulin" in cl.lower():
                return {
                    "has_insulin": False,
                    "evidence": f"Profile explicitly notes cleared history: '{cl}'.",
                    "confidence": 1.0
                }

        # Check raw text for clear negation
        text_lower = clinical_text.lower()
        if "never required insulin" in text_lower or "no history of insulin" in text_lower or "not on insulin" in text_lower:
            return {
                "has_insulin": False,
                "evidence": "Clinical text explicitly states patient has no insulin history.",
                "confidence": 0.95
            }
        elif "insulin therapy" in text_lower or "on basal insulin" in text_lower:
            return {
                "has_insulin": True,
                "evidence": "Clinical text mentions active or prior insulin therapy.",
                "confidence": 0.90
            }

        return {
            "has_insulin": False,
            "evidence": "No insulin medications recorded in profile.",
            "confidence": 0.80
        }

