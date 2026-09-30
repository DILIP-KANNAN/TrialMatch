"""
Generates 50 rich, realistic synthetic clinical records for TrialMatch 2.0.
Each record contains both raw doctor notes and structured EHR profiles.
"""

import json
import random
import os

NAMES = [
    ("Evelyn Harper", "female", 52), ("Marcus Vance", "male", 45), ("Arthur Pendelton", "male", 68),
    ("Sarah Jenkins", "female", 34), ("Robert Miller", "male", 60), ("Diana Prince", "female", 48),
    ("Thomas Shelby", "male", 55), ("Chloe Bennet", "female", 29), ("Walter White", "male", 72),
    ("Elena Rostova", "female", 38), ("David Kim", "male", 50), ("Grace Hopper", "female", 42),
    ("Henry Higgins", "male", 65), ("Maya Lin", "female", 36), ("Julian Thorne", "male", 58),
    ("Natalie Dormer", "female", 41), ("Christopher Lee", "male", 62), ("Miriam Fox", "female", 70),
    ("Alexander Ross", "male", 47), ("Hannah Abbott", "female", 53), ("Victor Stone", "male", 39),
    ("Clara Oswald", "female", 44), ("Patrick Stewart", "male", 69), ("Jessica Jones", "female", 33),
    ("Anthony Stark", "male", 59), ("Barbara Gordon", "female", 46), ("Jonathan Kent", "male", 51),
    ("Eleanor Vance", "female", 63), ("Benjamin Sisko", "male", 40), ("Rachel Green", "female", 54),
    ("Ethan Hunt", "male", 37), ("Monica Geller", "female", 49), ("James Gordon", "male", 61),
    ("Lily Evans", "female", 28), ("Richard Castle", "male", 66), ("Dana Scully", "female", 43),
    ("Fox Mulder", "male", 57), ("Donna Noble", "female", 52), ("Charles Xavier", "male", 64),
    ("Peggy Carter", "female", 35), ("Luke Skywalker", "male", 48), ("Jean Grey", "female", 55),
    ("Bruce Banner", "male", 69), ("Wanda Maximoff", "female", 31), ("Peter Parker", "male", 58),
    ("Gwen Stacy", "female", 50), ("Stephen Strange", "male", 62), ("Natasha Romanoff", "female", 39),
    ("Steve Rogers", "male", 53), ("Carol Danvers", "female", 67)
]

def generate_patients():
    patients = []
    
    for idx, (name, gender, base_age) in enumerate(NAMES, start=1):
        pid = f"P{idx:03d}"
        age = base_age
        
        # Clinical profiles variations
        # 1. Insulin history distribution: ~25% on insulin
        has_insulin = (idx % 4 == 0)
        # 2. Kidney disease distribution: ~15% have CKD
        has_ckd = (idx % 7 == 0)
        # 3. Heart failure / CAD: ~15%
        has_cad = (idx % 6 == 0)
        # 4. Neuropathy: ~20%
        has_neuropathy = (idx % 5 == 0)
        # 5. Missing eGFR: ~25%
        missing_egfr = (idx % 3 == 0)
        # 6. Hypertension: ~50%
        has_htn = (idx % 2 == 0)
        
        hba1c = round(random.uniform(6.6, 9.4), 1)
        bmi = round(random.uniform(24.5, 36.5), 1)
        
        if has_ckd:
            egfr_val = round(random.uniform(32.0, 48.0), 1)
        elif missing_egfr:
            egfr_val = None
        else:
            egfr_val = round(random.uniform(65.0, 98.0), 1)
            
        # Build conditions
        conditions = [{"name": "Type 2 Diabetes Mellitus", "synonyms": ["T2D", "NIDDM"], "duration_years": random.randint(2, 10)}]
        if has_htn:
            conditions.append({"name": "Essential Hypertension", "status": "controlled"})
        if has_ckd:
            conditions.append({"name": "Chronic Kidney Disease", "status": "moderate renal impairment"})
        if has_cad:
            conditions.append({"name": "Coronary Artery Disease", "status": "stable"})
        if has_neuropathy:
            conditions.append({"name": "Diabetic Peripheral Neuropathy", "status": "mild sensory impairment"})
            
        # Build medications
        meds = []
        if has_insulin:
            meds.append({"name": "Insulin Glargine (Lantus)", "drug_class": "Long-Acting Insulin", "dose": "20 units QHS"})
            meds.append({"name": "Metformin", "drug_class": "Biguanide", "dose": "1000mg BID"})
        else:
            meds.append({"name": "Metformin", "drug_class": "Biguanide", "dose": "1000mg BID"})
            if idx % 3 == 1:
                meds.append({"name": "Sitagliptin (Januvia)", "drug_class": "DPP-4 Inhibitor", "dose": "100mg daily"})
                
        if has_htn:
            meds.append({"name": "Lisinopril", "drug_class": "ACE Inhibitor", "dose": "10mg daily"})
            
        # Build raw text narrative
        insulin_text = "Patient is currently managed on basal insulin therapy." if has_insulin else "Patient has been maintained on oral agents and has never required insulin therapy."
        ckd_text = f"Renal assessment indicates chronic kidney impairment with eGFR of {egfr_val} mL/min/1.73m2." if has_ckd else ("Recent renal function and eGFR labs are not on file." if missing_egfr else f"Renal function is preserved with eGFR {egfr_val} mL/min/1.73m2.")
        cad_text = "Medical history is notable for coronary artery disease." if has_cad else "No prior history of myocardial infarction or congestive heart failure."
        neuro_text = "Patient reports bilateral burning sensation and tingling in feet consistent with diabetic peripheral neuropathy." if has_neuropathy else "Neurological exam normal with no peripheral sensory deficits."
        
        narrative = (
            f"{name} is a {age}-year-old {gender} with established Type 2 Diabetes Mellitus. "
            f"Recent laboratory panel demonstrates an HbA1c of {hba1c}% and a calculated BMI of {bmi} kg/m2. "
            f"{insulin_text} {ckd_text} {cad_text} {neuro_text} "
            f"Current regimen includes {', '.join(m['name'] for m in meds)}."
        )
        
        cleared = []
        if not has_insulin:
            cleared.append("prior insulin exposure")
        if not has_cad:
            cleared.append("heart failure / acute coronary events")
        if not has_ckd:
            cleared.append("active kidney disease")
            
        patient_record = {
            "patient_id": pid,
            "name": name,
            "clinical_text": narrative,
            "structured_profile": {
                "demographics": {
                    "age": age,
                    "gender": gender
                },
                "conditions": conditions,
                "labs": {
                    "HbA1c": {"value": hba1c, "unit": "%", "recent": True},
                    "BMI": {"value": bmi, "unit": "kg/m2", "recent": True},
                    "eGFR": {"value": egfr_val, "unit": "mL/min/1.73m2", "status": "missing" if egfr_val is None else "recorded"}
                },
                "medications": meds,
                "contraindications_cleared": cleared
            }
        }
        patients.append(patient_record)
        
    return patients

if __name__ == "__main__":
    random.seed(42)
    pts = generate_patients()
    out_path = os.path.join(os.path.dirname(__file__), "patients.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(pts, f, indent=2)
    print(f"Generated {len(pts)} patient records in {out_path}.")
