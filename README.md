# TrialMatch 2.0: Population-Scale Agentic Clinical Trial Matching Engine

TrialMatch 2.0 is an autonomous, multi-agent AI system designed to discover, verify, and prioritize clinical trial opportunities across an entire hospital patient population. Moving beyond simple one-to-one classifiers, TrialMatch operates at population scale ($N \text{ Patients} \leftrightarrow M \text{ Trials}$) using a goal-driven **Matchmaker Orchestrator**, a **2-Stage Coarse-to-Fine Retrieval Layer**, specialized reasoning tools (including fine-tuned **BioBERT NLI**), and a **Tri-State Clinical Safety Auditor**.

---

## 🎯 The Paradigm Shift

### Legacy Approach vs. Agentic Platform
* **Legacy 1-to-1 Matching:** Evaluated a single patient against a single trial via a fixed pipeline (`Regex -> BioBERT -> Avg Score`). It suffered from $O(N \times M)$ computational explosion and lacked reasoning transparency.
* **TrialMatch 2.0 Agentic Matching:** Given a hospital patient database (50–1000+ records) and an active trial registry (10–100+ protocols), an autonomous **Matchmaker Orchestrator** plans and executes coarse-to-fine candidate discovery, deep multi-tool evidence verification, clinical safety gap detection, and dual-view prioritization.

```
                    ┌─────────────────────────┐
                    │ HOSPITAL PATIENT DB (N) │
                    └────────────┬────────────┘
                                 │
                                 ↓
                     ┌───────────────────────┐
                     │   Patient Profiler    │
                     └───────────┬───────────┘
                                 │
                                 ↓
                         Patient Profiles
                                 │
┌────────────────────┐           │
│ ACTIVE TRIALS (M)  │───────────┘
└─────────┬──────────┘
          ↓
┌────────────────────┐
│   Trial Analyzer   │
└─────────┬──────────┘
          ↓
   Atomic Criteria
          │
          ↓
┌────────────────────────────────────────────────────────┐
│               MATCHMAKER ORCHESTRATOR                  │
│   Goal: "Discover, verify, and prioritize matches"    │
└───────────────────────────┬────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            ↓                               ↓
   Stage 1: Coarse Filter          Stage 2: Deep NLP
   (Demographics, Condition,        (Evidence Agent +
    Lab Boundary Pruning)            Tool Suite)
            │                               │
            └───────────────┬───────────────┘
                            ↓
                     Clinical Auditor
              (Tri-State: PASS / FAIL / UNKNOWN)
                            ↓
            ┌───────────────┴───────────────┐
            ↓                               ↓
      High-Confidence              Needs Verification
      (Ready for Trial)            (Missing Lab Flagged)
            │                               │
            └───────────────┬───────────────┘
                            ↓
                 Agentic Control Room
               (Dual-View React Portal)
```

---

## 🏗️ Core Architecture & Agentic Workflow

### 1. Matchmaker Orchestrator (`Backend/agent/orchestrator.py`)
The central executive agent given an autonomous objective:
> *"Find all potentially suitable patients for available trials, verify eligibility with exact evidence, and audit clinical risks."*

The orchestrator dynamically coordinates sub-agents and tools rather than following a rigid script.

### 2. Stage 1: Coarse-to-Fine Candidate Retrieval (`Backend/tools/retrieval_tool.py`)
To prevent evaluating tens of thousands of comparisons with heavy neural networks, Stage 1 uses fast, low-compute filtering:
1. **Target Condition Match:** Discards patients whose diagnoses do not overlap with the trial's therapeutic area.
2. **Age & Demographic Bounds:** Prunes patients outside protocol inclusion windows.
3. **Known Lab Thresholds:** Rapidly screens out patients with disqualifying HbA1c, BMI, or eGFR values.
4. **Primary Contraindication Screening:** Discards candidates with immediate disqualifiers (e.g. active insulin history for non-insulin trials).

*Result:* Pruned **56%** of candidate pairs instantaneously before invoking deep NLP.

### 3. Specialized Reasoning Tool Suite (`Backend/tools/`)
BioBERT is no longer a monolithic match scorer; it is a **specialized tool** called only when semantic reasoning is required:
* **`BioBERTTool` (`tools/biobert_tool.py`):** Transfer-learning NLI engine (fine-tuned on SNLI/Biomedical data) with sentence lexical pre-ranking and LRU inference caching. Evaluates semantic entailment vs. contradiction.
* **`NumericTool` (`tools/numeric_tool.py`):** Relational (`>`, `<`, `>=`, `<=`, `between`) and interval algebra for clinical laboratory values and age criteria.
* **`TerminologyTool` (`tools/terminology_tool.py`):** Medical ontology normalizer mapping clinical synonyms (*NIDDM $\leftrightarrow$ Type 2 Diabetes*, *Renal Impairment $\leftrightarrow$ Kidney Disease*) and drug classes (*Metformin $\rightarrow$ Biguanide*, *Lantus $\rightarrow$ Long-acting Insulin*).

### 4. Tri-State Clinical Safety Auditor (`Backend/agent/auditor.py`)
Replaces binary Yes/No matches with clinical reality:
* **`PASS`:** Criteria satisfied with verified clinical evidence.
* **`FAIL`:** Criteria definitively violated or contraindicated.
* **`UNKNOWN`:** Clinical documentation gap or missing laboratory test.

#### Output Tiers:
* 🟢 **`HIGH`:** Patient satisfies all inclusion and exclusion criteria with verified evidence.
* 🟡 **`NEEDS VERIFICATION`:** High-potential candidate meeting all verified criteria, but missing a key metric (e.g., eGFR lab unavailable, pregnancy status unrecorded). Action items are autonomously generated for the physician.
* 🔴 **`NOT SUITABLE`:** Candidate excluded due to criteria violation or hard contraindication.

---

## 🖥️ Agentic Control Room Frontend (`frontend/src/TrialMatch.jsx`)

The React application provides a clinical command center:
1. **Fleet KPI Ribbon:** Real-time pulse showing Total Active Protocols (10), Patient Cohort (50), Assessed Pairs (220), High Matches (164), Needs Verification (25), and Excluded (31).
2. **Live Matchmaker Thought Console:** Real-time streaming log of the agent's internal reasoning and execution steps.
3. **Dual-View Operational Hub:**
   * **Trial-Centric View:** Select any clinical trial to view its ranked candidate leaderboard with tier filters and status badges.
   * **Patient-Centric View:** Select any patient to inspect their matched trial opportunities ranked by readiness score.
4. **Explainable Evidence & Audit Drawer:** Deep modal showing atomic criteria breakdown, extracted raw EHR sentence quotes, BioBERT NLI confidence percentages, and physician action items.

---

## 📁 Repository Structure

```plaintext
.
├── Architecture_Report.md          # Deep technical AI & transfer learning report
├── README.md                       # Main project documentation
│
├── Backend/
│   ├── app.py                      # Flask REST API with cached fleet endpoints
│   ├── train_nli.py                # BioBERT NLI transfer learning training script
│   ├── test_orchestrator.py        # Population-scale orchestrator benchmark test
│   ├── test_tools.py               # Tool suite unit tests
│   │
│   ├── agent/                      # Core Orchestration Engine
│   │   ├── orchestrator.py         # Matchmaker Orchestrator
│   │   ├── auditor.py              # Clinical Safety Auditor (Tri-State logic)
│   │   └── state.py                # Data contracts & Pydantic/dataclass schemas
│   │
│   ├── agents/                     # Sub-Agents
│   │   └── evidence_agent.py       # Atomic criteria evaluator & sentence extractor
│   │
│   ├── tools/                      # Specialized Reasoning Tool Suite
│   │   ├── biobert_tool.py         # Fine-tuned BioBERT NLI inference & caching
│   │   ├── numeric_tool.py         # Relational & interval math evaluator
│   │   ├── terminology_tool.py     # Medical synonym & drug ontology mapper
│   │   └── retrieval_tool.py       # Stage 1 coarse retrieval filter
│   │
│   ├── data/                       # Standardized Population Datasets
│   │   ├── generate_data.py        # Synthetic EHR cohort generator
│   │   ├── patients.json           # 50 rich patient records (notes + structured EHR)
│   │   └── trials.json             # 10 clinical trials with atomic criteria
│   │
│   └── biobert_nli_finetuned/      # Pre-trained BioBERT model weights & config
│
└── frontend/                       # React Agentic Control Room
    ├── package.json
    ├── tailwind.config.js
    └── src/
        ├── TrialMatch.jsx          # Dual-view Control Room dashboard
        ├── App.js
        └── index.css
```

---

## 🚀 Getting Started

### 1. Prerequisites
* Python 3.10+
* Node.js 18+ and npm
* Recommended: NVIDIA GPU with CUDA for local BioBERT acceleration (CPU fallback supported)

### 2. Backend Setup
Navigate to the `Backend` directory:
```bash
cd Backend
```

Install the dependencies:
```bash
pip install flask flask-cors torch transformers datasets evaluate accelerate scikit-learn
```

Run unit tests to verify the tool suite:
```bash
python test_tools.py
```

Run the population-scale benchmark test:
```bash
python test_orchestrator.py
```

Start the Flask API server:
```bash
python app.py
```
*(The backend will start at `http://127.0.0.1:5000` with pre-cached fleet matchmaking results)*

### 3. Frontend Setup
Open a second terminal and navigate to `frontend`:
```bash
cd frontend
npm install
npm start
```
*(The browser will automatically open `http://localhost:3000`)*

---

## 📊 Benchmark & Performance

Tested on a cohort of **50 patients** across **10 active clinical trials**:
* **Theoretical Comparison Space:** $50 \times 10 = 500$ pairs
* **Stage 1 Pruning:** Reduced to **220 candidate pairs** (56% search space reduction)
* **Total Execution Time:** **21.79 seconds** on CPU (instantaneous when cached)
* **High-Confidence Matches:** 164 pairs
* **Needs Verification (Missing Labs Identified):** 25 pairs
* **Excluded / Contraindicated:** 31 pairs

---

## 🛠️ Technology Stack
* **Language & Frameworks:** Python 3.11, Flask, React 19, Tailwind CSS
* **NLP & Deep Learning:** PyTorch, Hugging Face Transformers (`BioBERT`), SNLI Dataset
* **Architecture:** Multi-Agent Cognitive Orchestrator, Coarse-to-Fine Retrieval, Tri-State Clinical Verification
