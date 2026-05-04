import json

# ----------------------------
# Load Data
# ----------------------------
def load_data():
    with open(r"C:\Users\dilip\Downloads\NLP mini project\Backend\patients.json") as f:
        patients = json.load(f)
    with open(r"C:\Users\dilip\Downloads\NLP mini project\Backend\trials.json") as f:
        trials = json.load(f)
    return patients, trials


# ----------------------------
# Rule Evaluation Functions
# ----------------------------

def check_age(rule, patient):
    age = patient.get("age")
    if "between" in rule:
        parts = rule.split("between")[1].strip().split("and")
        low, high = int(parts[0]), int(parts[1])
        return low <= age <= high
    return False


def check_hba1c(rule, patient):
    hba1c = patient.get("HbA1c")
    
    if ">" in rule:
        val = float(rule.split(">")[1])
        return hba1c > val
    
    if "between" in rule:
        parts = rule.split("between")[1].strip().split("and")
        low, high = float(parts[0]), float(parts[1])
        return low <= hba1c <= high
    
    return False


def check_bmi(rule, patient):
    bmi = patient.get("BMI")
    if ">" in rule:
        val = float(rule.split(">")[1])
        return bmi > val
    return False


def check_condition(rule, patient):
    return rule.lower() in patient.get("condition", "").lower()


def check_insulin(rule, patient):
    if "No insulin" in rule:
        return not patient.get("insulin_history", False)
    if "Insulin" in rule:
        return patient.get("insulin_history", False)
    return True


def check_exclusion(rule, patient):
    return rule.lower() not in [c.lower() for c in patient.get("conditions", [])]


# ----------------------------
# Core Matching Logic
# ----------------------------

def evaluate_rule(rule, patient):
    if "Age" in rule:
        return check_age(rule, patient), "Age"
    
    elif "HbA1c" in rule:
        return check_hba1c(rule, patient), "HbA1c"
    
    elif "BMI" in rule:
        return check_bmi(rule, patient), "BMI"
    
    elif "Diabetes" in rule:
        return check_condition(rule, patient), "Condition"
    
    elif "insulin" in rule.lower():
        return check_insulin(rule, patient), "Insulin"
    
    return False, "Unknown"


def match_patient_to_trial(patient, trial):
    results = []
    matched = 0
    total = 0

    # Inclusion rules
    for rule in trial["inclusion"]:
        total += 1
        res, rule_type = evaluate_rule(rule, patient)
        results.append((rule, res))
        if res:
            matched += 1

    # Exclusion rules (must NOT match)
    for rule in trial["exclusion"]:
        total += 1
        res = check_exclusion(rule, patient)
        results.append((f"NOT {rule}", res))
        if res:
            matched += 1

    score = matched / total
    is_match = score >= 0.7  # threshold

    return is_match, score, results


# ----------------------------
# Explanation Generator
# ----------------------------

def generate_explanation(results):
    explanation = []
    
    for rule, passed in results:
        if passed:
            explanation.append(f"✔ {rule}")
        else:
            explanation.append(f"✖ {rule}")
    
    return explanation


# ----------------------------
# Run Matching
# ----------------------------

def run_matching():
    patients, trials = load_data()

    for patient in patients[:5]:  # test first 5 patients
        print(f"\n🧑 Patient ID: {patient['id']}")
        
        for trial in trials:
            is_match, score, results = match_patient_to_trial(patient, trial)
            
            if is_match:
                print(f"\n✅ MATCH with Trial {trial['trial_id']}")
                print(f"Score: {round(score, 2)}")
                
                explanation = generate_explanation(results)
                for line in explanation:
                    print(line)


if __name__ == "__main__":
    run_matching()