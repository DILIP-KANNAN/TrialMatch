# TrialMatch: AI Clinical Trial Matching Engine

TrialMatch is a full-stack, AI-driven application designed to dynamically match unstructured patient clinical notes to complex clinical trial criteria. It leverages **Natural Language Inference (NLI)** via a fine-tuned BioBERT model to logically deduce patient eligibility.

---

## 🎯 What We Are Trying To Do

Matching patients to clinical trials is notoriously difficult because:
1. Doctors write **unstructured clinical notes**, making it hard for traditional software to parse.
2. Clinical trial criteria require **logical reasoning** (e.g., understanding that "renal failure" entails "kidney disease", or recognizing that "no prior insulin" contradicts "patient is currently on basal insulin").

**Our Goal:** Build an intelligent system that reads a raw paragraph of doctor's notes and logically infers whether the patient meets the specific inclusion and exclusion criteria of a trial.

---

## 🏗️ Implementation Strategy & Evolution

We approached this problem in three distinct evolutionary phases:

### Phase 1: The Legacy Rule-Based System
* **How it worked:** The frontend forced doctors to use strict dropdowns and numerical inputs (Age, HbA1c, BMI). The backend used hardcoded Python regex (`re.search`) to check these numbers, and a raw `dmis-lab/biobert-base-cased-v1.1` model to calculate basic "cosine similarity" between the text.
* **The Problem:** It only worked for specific, hardcoded diseases. Furthermore, cosine similarity is terrible at logical matching (e.g., if a trial excludes Kidney Disease, and the patient *has* Kidney Disease, cosine similarity outputs a *high* score because the vocabulary overlaps, which is the exact opposite of what we want!).

### Phase 2: Transfer Learning (The NLI Upgrade)
* **How it worked:** We realized the AI needed to understand **Entailment vs. Contradiction**. We wrote a custom PyTorch training script (`train_nli.py`) to fine-tune the BioBERT model on an NLI dataset (SNLI) using an RTX 4060 GPU. 
* **The Result:** The model learned to read a Premise (Patient Text) and a Hypothesis (Trial Criterion) and accurately predict whether the patient logically satisfies the rule. 

### Phase 3: The Hybrid Engine (Unstructured Input)
* **How it worked:** 
  1. We completely redesigned the React frontend to accept **unstructured, raw clinical notes** (paragraphs of text) instead of strict forms.
  2. Because NLI Language Models are notoriously bad at pure mathematics (e.g., knowing if `45` is between `30` and `60`), we implemented a **Hybrid Router** in Flask. 
* **The Result:** When evaluating a trial:
  * **Math Criteria** (e.g., "Age 30-60") bypass the AI. A Python regex engine dynamically extracts numbers from the clinical note and evaluates the math.
  * **Semantic Criteria** (e.g., "Active infection") are routed to the fine-tuned BioBERT model to logically deduce Entailment vs. Contradiction.

---

## 🚀 How to Run the Application

### 1. Backend Setup (Flask & PyTorch)
Navigate to the `Backend` directory:
```bash
cd Backend
```

Install the required Python packages in your conda/virtual environment:
```bash
pip install flask flask-cors torch torchvision torchaudio transformers datasets evaluate accelerate scikit-learn
```

If you haven't trained the NLI model yet, run the transfer learning script (Requires GPU):
```bash
python train_nli.py
```

Start the Flask API server:
```bash
python app.py
```
*(The backend will run on `http://localhost:5000`)*

### 2. Frontend Setup (React & Tailwind)
Open a new terminal and navigate to the `frontend` directory:
```bash
cd frontend
```

Install dependencies and start the development server:
```bash
npm install
npm start
```
*(The frontend will automatically open at `http://localhost:3000`)*

---

## 🛠️ Tech Stack
* **Frontend:** React, Tailwind CSS, Javascript
* **Backend:** Python, Flask
* **AI/Machine Learning:** PyTorch, Hugging Face `transformers` (BioBERT), Hugging Face `datasets`
