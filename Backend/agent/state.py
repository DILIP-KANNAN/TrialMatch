"""
State and Data Contracts for TrialMatch 2.0 Agentic Architecture.
Defines patient profiles, trial atomic criteria, evaluation results, and matchmaker states.
"""

from typing import List, Dict, Any, Optional, Union, Literal
from dataclasses import dataclass, field

# ==========================================
# Patient Representation
# ==========================================

@dataclass
class Demographics:
    age: int
    gender: Literal["male", "female", "other"]

@dataclass
class ConditionItem:
    name: str
    synonyms: List[str] = field(default_factory=list)
    duration_years: Optional[float] = None
    status: Optional[str] = None # e.g. "active", "controlled"

@dataclass
class LabItem:
    value: Optional[float] = None
    unit: str = ""
    status: Optional[str] = None # e.g. "normal", "elevated", "missing"
    recent: bool = True

@dataclass
class MedicationItem:
    name: str
    drug_class: Optional[str] = None
    dose: Optional[str] = None

@dataclass
class StructuredPatientProfile:
    demographics: Demographics
    conditions: List[ConditionItem] = field(default_factory=list)
    labs: Dict[str, LabItem] = field(default_factory=dict)
    medications: List[MedicationItem] = field(default_factory=list)
    contraindications_cleared: List[str] = field(default_factory=list)

@dataclass
class PatientRecord:
    patient_id: str
    name: str
    clinical_text: str
    structured_profile: StructuredPatientProfile


# ==========================================
# Trial Criteria Representation
# ==========================================

CriteriaClause = Literal["inclusion", "exclusion"]
CriteriaType = Literal["numeric", "semantic", "terminology", "temporal"]
EvaluationStatus = Literal["PASS", "FAIL", "UNKNOWN"]
MatchTier = Literal["HIGH", "NEEDS VERIFICATION", "NOT SUITABLE"]

@dataclass
class AtomicCriterion:
    id: str
    clause: CriteriaClause # "inclusion" or "exclusion"
    type: CriteriaType # "numeric", "semantic", "terminology", "temporal"
    description: str
    # Numeric specific
    field: Optional[str] = None # e.g. "age", "HbA1c", "BMI", "eGFR"
    operator: Optional[str] = None # ">", "<", ">=", "<=", "between", "=="
    value: Optional[Union[float, List[float]]] = None
    unit: Optional[str] = None
    # Semantic / Terminology specific
    concept: Optional[str] = None
    negated: bool = False
    # Temporal specific
    duration_months_min: Optional[float] = None

@dataclass
class ClinicalTrialProtocol:
    trial_id: str
    name: str
    phase: str
    target_condition: str
    summary: str
    criteria: List[AtomicCriterion] = field(default_factory=list)


# ==========================================
# Evaluation & Evidence Contracts
# ==========================================

@dataclass
class CriterionEvaluation:
    criterion_id: str
    rule_description: str
    clause: CriteriaClause
    status: EvaluationStatus # "PASS", "FAIL", "UNKNOWN"
    evidence_quote: str # Quote from clinical text or lab value reference
    tool_used: str # "numeric_tool", "biobert_tool", "terminology_tool", "temporal_tool", "auditor_gap_detector"
    confidence: float # 0.0 - 1.0
    details: Dict[str, Any] = field(default_factory=dict)
    action_required: Optional[str] = None # For UNKNOWN/missing labs

@dataclass
class MatchAssessment:
    match_id: str
    patient_id: str
    trial_id: str
    tier: MatchTier # "HIGH", "NEEDS VERIFICATION", "NOT SUITABLE"
    match_score: float # 0 - 100
    summary: str
    criteria_evaluations: List[CriterionEvaluation] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    created_at: Optional[str] = None


# ==========================================
# Fleet / Population State Contracts
# ==========================================

@dataclass
class MatchmakerFleetResult:
    total_patients: int
    total_trials: int
    total_evaluated_pairs: int
    high_match_count: int
    verification_needed_count: int
    excluded_count: int
    by_trial: Dict[str, List[Dict[str, Any]]] # trial_id -> ranked candidate list
    by_patient: Dict[str, List[Dict[str, Any]]] # patient_id -> ranked trial opportunities
    execution_logs: List[str] = field(default_factory=list)
