import React, { useState, useEffect } from "react";

// ==========================================
// Fallback Datasets (In case backend is booting)
// ==========================================
const FALLBACK_TRIALS = [
  {
    trial_id: "T01",
    name: "DIAMOND-MET Study",
    phase: "Phase III",
    target_condition: "Type 2 Diabetes",
    summary: "Evaluating novel dual-action GLP-1/GIP agonists in adult Type 2 Diabetes patients without insulin exposure.",
    criteria: [
      { id: "C01_1", clause: "inclusion", type: "numeric", field: "age", operator: "between", value: [40, 65], description: "Age between 40 and 65 years inclusive" },
      { id: "C01_2", clause: "inclusion", type: "numeric", field: "HbA1c", operator: ">", value: 7.0, description: "Baseline HbA1c > 7.0%" },
      { id: "C01_3", clause: "inclusion", type: "semantic", concept: "Patient has no history of prior insulin therapy", description: "No prior exposure to insulin therapy" },
      { id: "C01_4", clause: "exclusion", type: "semantic", concept: "Patient has active kidney disease or severe renal impairment", description: "History of chronic kidney disease or renal failure" },
      { id: "C01_5", clause: "exclusion", type: "semantic", concept: "Patient has heart failure or congestive cardiac failure", description: "Documented heart failure" }
    ]
  },
  {
    trial_id: "T02",
    name: "GLUCO-GUARD Cardiovascular Safety Trial",
    phase: "Phase IV",
    target_condition: "Type 2 Diabetes",
    summary: "Assessing cardiovascular outcomes and renal preservation in overweight patients with elevated HbA1c.",
    criteria: [
      { id: "C02_1", clause: "inclusion", type: "numeric", field: "age", operator: "between", value: [30, 70], description: "Age between 30 and 70 years" },
      { id: "C02_2", clause: "inclusion", type: "numeric", field: "BMI", operator: ">=", value: 27.0, description: "BMI >= 27.0 kg/m2 (overweight or obese)" },
      { id: "C02_3", clause: "inclusion", type: "numeric", field: "HbA1c", operator: "between", value: [6.5, 9.5], description: "HbA1c between 6.5% and 9.5%" },
      { id: "C02_4", clause: "exclusion", type: "semantic", concept: "Patient is pregnant or planning pregnancy", description: "Pregnancy or lactation" },
      { id: "C02_5", clause: "exclusion", type: "semantic", concept: "Patient has liver disease, cirrhosis or acute hepatic injury", description: "Active liver disease" }
    ]
  },
  {
    trial_id: "T03",
    name: "RENAL-SAVE Diabetic Nephropathy Trial",
    phase: "Phase IIb",
    target_condition: "Type 2 Diabetes",
    summary: "Targeted renal protective therapy in patients with diabetic kidney involvement and controlled glycemic status.",
    criteria: [
      { id: "C03_1", clause: "inclusion", type: "numeric", field: "age", operator: "between", value: [45, 75], description: "Age between 45 and 75 years" },
      { id: "C03_2", clause: "inclusion", type: "numeric", field: "HbA1c", operator: "<=", value: 9.0, description: "HbA1c <= 9.0%" },
      { id: "C03_3", clause: "inclusion", type: "numeric", field: "eGFR", operator: "between", value: [30, 60], description: "Moderate renal impairment with eGFR between 30 and 60 mL/min/1.73m2" },
      { id: "C03_4", clause: "exclusion", type: "semantic", concept: "Patient has end stage renal disease or is on dialysis", description: "End-stage renal disease (ESRD) or active hemodialysis" },
      { id: "C03_5", clause: "exclusion", type: "semantic", concept: "Patient had a recent stroke or acute cerebrovascular accident", description: "Stroke within past 6 months" }
    ]
  },
  {
    trial_id: "T04",
    name: "MET-CONTROL 2026 Intensive Monotherapy",
    phase: "Phase III",
    target_condition: "Type 2 Diabetes",
    summary: "Evaluating once-weekly insulin sensitizer add-on for patients sub-optimally controlled on Metformin alone.",
    criteria: [
      { id: "C04_1", clause: "inclusion", type: "numeric", field: "age", operator: "between", value: [35, 65], description: "Age between 35 and 65 years" },
      { id: "C04_2", clause: "inclusion", type: "numeric", field: "HbA1c", operator: "between", value: [7.0, 8.5], description: "HbA1c between 7.0% and 8.5%" },
      { id: "C04_3", clause: "inclusion", type: "semantic", concept: "Patient is actively taking Metformin therapy", description: "Current stable Metformin therapy" },
      { id: "C04_4", clause: "exclusion", type: "semantic", concept: "Patient has previous history of insulin therapy", description: "Prior insulin exposure" },
      { id: "C04_5", clause: "exclusion", type: "numeric", field: "eGFR", operator: "<", value: 45, description: "eGFR < 45 mL/min/1.73m2" }
    ]
  },
  {
    trial_id: "T05",
    name: "CARDIO-VASC Dual Protection Initiative",
    phase: "Phase III",
    target_condition: "Type 2 Diabetes",
    summary: "Cardiovascular risk reduction in diabetic patients with comorbid hypertension.",
    criteria: [
      { id: "C05_1", clause: "inclusion", type: "numeric", field: "age", operator: "between", value: [45, 80], description: "Age between 45 and 80 years" },
      { id: "C05_2", clause: "inclusion", type: "semantic", concept: "Patient has diagnosed hypertension or elevated blood pressure", description: "Documented hypertension" },
      { id: "C05_3", clause: "inclusion", type: "numeric", field: "HbA1c", operator: ">=", value: 7.0, description: "HbA1c >= 7.0%" },
      { id: "C05_4", clause: "exclusion", type: "semantic", concept: "Patient had acute myocardial infarction or cardiac arrest", description: "History of acute myocardial infarction" }
    ]
  }
];

export default function TrialMatch() {
  const [activeTab, setActiveTab] = useState("trial-centric"); // 'trial-centric' | 'patient-centric' | 'patients' | 'trials'
  const [fleetResults, setFleetResults] = useState(null);
  const [patients, setPatients] = useState([]);
  const [trials, setTrials] = useState(FALLBACK_TRIALS);
  const [selectedTrialId, setSelectedTrialId] = useState("T01");
  const [selectedPatientId, setSelectedPatientId] = useState("P001");
  const [inspectedMatch, setInspectedMatch] = useState(null); // Match assessment object for Drawer
  const [isLoading, setIsLoading] = useState(false);
  const [isConsoleOpen, setIsConsoleOpen] = useState(true);
  const [tierFilter, setTierFilter] = useState("ALL"); // 'ALL' | 'HIGH' | 'NEEDS VERIFICATION' | 'NOT SUITABLE'
  const [searchQuery, setSearchQuery] = useState("");
  const [backendConnected, setBackendConnected] = useState(false);

  // Load Initial Fleet Results
  useEffect(() => {
    fetchFleetResults();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchFleetResults = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:5000/api/fleet/results");
      if (!res.ok) throw new Error("Backend response error");
      const data = await res.json();
      setFleetResults(data);
      setBackendConnected(true);

      // Also fetch full patient records if available
      const ptsRes = await fetch("http://127.0.0.1:5000/api/fleet/patients");
      if (ptsRes.ok) {
        const ptsData = await ptsRes.json();
        setPatients(ptsData);
      }

      // Also fetch full trials if available
      const trsRes = await fetch("http://127.0.0.1:5000/api/fleet/trials");
      if (trsRes.ok) {
        const trsData = await trsRes.json();
        setTrials(trsData);
      }
    } catch (err) {
      console.warn("Backend not reached or booting up, initializing local simulation:", err);
      setBackendConnected(false);
      // Auto-generate realistic demo state if backend is still initializing
      generateDemoFleet();
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunFleet = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:5000/api/fleet/run", { method: "POST" });
      if (!res.ok) throw new Error("Failed to run fleet");
      const json = await res.json();
      setFleetResults(json.data);
      setBackendConnected(true);
    } catch (err) {
      console.warn("Run fleet failed, refreshing local state:", err);
      generateDemoFleet();
    } finally {
      setIsLoading(false);
    }
  };

  const generateDemoFleet = () => {
    // Generates a mock fleet result if offline
    const demoCandidates = [
      {
        match_id: "M_P001_T01",
        patient_id: "P001",
        patient_name: "Evelyn Harper",
        trial_id: "T01",
        trial_name: "DIAMOND-MET Study",
        tier: "HIGH",
        match_score: 100.0,
        summary: "High-confidence match! Patient satisfies all 5 inclusion and exclusion criteria with verified evidence.",
        counts: { total: 5, passed: 5, failed: 0, unknown: 0 },
        action_items: [],
        critical_violations: [],
        criteria_evaluations: [
          { criterion_id: "C01_1", rule_description: "Age between 40 and 65", clause: "inclusion", status: "PASS", evidence_quote: "Patient age is 52 (satisfies between 40 and 65).", tool_used: "numeric_tool", confidence: 1.0 },
          { criterion_id: "C01_2", rule_description: "Baseline HbA1c > 7.0%", clause: "inclusion", status: "PASS", evidence_quote: "Patient HbA1c is 8.2% (> 7.0%).", tool_used: "numeric_tool", confidence: 1.0 },
          { criterion_id: "C01_3", rule_description: "No prior insulin therapy", clause: "inclusion", status: "PASS", evidence_quote: "Patient has been maintained on oral agents and has never required insulin therapy.", tool_used: "terminology_tool", confidence: 0.95 },
          { criterion_id: "C01_4", rule_description: "Exclusion: Kidney disease", clause: "exclusion", status: "PASS", evidence_quote: "Renal function is preserved with eGFR 84.0 mL/min/1.73m2.", tool_used: "terminology_tool", confidence: 1.0 },
          { criterion_id: "C01_5", rule_description: "Exclusion: Heart failure", clause: "exclusion", status: "PASS", evidence_quote: "No prior history of myocardial infarction or congestive heart failure.", tool_used: "biobert_tool", confidence: 0.98 }
        ]
      },
      {
        match_id: "M_P017_T01",
        patient_id: "P017",
        patient_name: "Christopher Lee",
        trial_id: "T01",
        trial_name: "DIAMOND-MET Study",
        tier: "NEEDS VERIFICATION",
        match_score: 83.0,
        summary: "Strong candidate meeting verified criteria, but requires laboratory verification for 1 unrecorded metric.",
        counts: { total: 5, passed: 4, failed: 0, unknown: 1 },
        action_items: ["Obtain laboratory test or documentation for eGFR."],
        critical_violations: [],
        criteria_evaluations: [
          { criterion_id: "C01_1", rule_description: "Age between 40 and 65", clause: "inclusion", status: "PASS", evidence_quote: "Patient age is 62.", tool_used: "numeric_tool", confidence: 1.0 },
          { criterion_id: "C01_2", rule_description: "Baseline HbA1c > 7.0%", clause: "inclusion", status: "PASS", evidence_quote: "HbA1c 8.4%.", tool_used: "numeric_tool", confidence: 1.0 },
          { criterion_id: "C01_3", rule_description: "No prior insulin therapy", clause: "inclusion", status: "PASS", evidence_quote: "No insulin history recorded.", tool_used: "terminology_tool", confidence: 0.95 },
          { criterion_id: "C01_4", rule_description: "Exclusion: Kidney disease", clause: "exclusion", status: "UNKNOWN", evidence_quote: "Recent renal function and eGFR labs are not on file.", tool_used: "auditor_gap_detector", confidence: 0.0, action_required: "Obtain laboratory test for eGFR." },
          { criterion_id: "C01_5", rule_description: "Exclusion: Heart failure", clause: "exclusion", status: "PASS", evidence_quote: "No history of heart failure.", tool_used: "biobert_tool", confidence: 0.94 }
        ]
      },
      {
        match_id: "M_P003_T01",
        patient_id: "P003",
        patient_name: "Arthur Pendelton",
        trial_id: "T01",
        trial_name: "DIAMOND-MET Study",
        tier: "NOT SUITABLE",
        match_score: 25.0,
        summary: "Candidate excluded due to 1 unmet/violated criterion(a). Primary reason: Age exceeds 65.",
        counts: { total: 5, passed: 3, failed: 2, unknown: 0 },
        action_items: [],
        critical_violations: ["Violated INCLUSION criterion: 'Age between 40 and 65'"],
        criteria_evaluations: [
          { criterion_id: "C01_1", rule_description: "Age between 40 and 65", clause: "inclusion", status: "FAIL", evidence_quote: "Patient age is 68 (fails between 40 and 65).", tool_used: "numeric_tool", confidence: 1.0 },
          { criterion_id: "C01_2", rule_description: "Baseline HbA1c > 7.0%", clause: "inclusion", status: "PASS", evidence_quote: "HbA1c 9.1%.", tool_used: "numeric_tool", confidence: 1.0 },
          { criterion_id: "C01_3", rule_description: "No prior insulin therapy", clause: "inclusion", status: "FAIL", evidence_quote: "Patient is managed on basal insulin (Lantus).", tool_used: "terminology_tool", confidence: 1.0 }
        ]
      }
    ];

    setFleetResults({
      total_patients: 50,
      total_trials: 10,
      total_evaluated_pairs: 220,
      high_match_count: 164,
      verification_needed_count: 25,
      excluded_count: 31,
      by_trial: { T01: demoCandidates },
      by_patient: { P001: [demoCandidates[0]] },
      execution_logs: [
        "[Matchmaker] Initialized fleet run with 50 patient records and 10 active trials.",
        "[Retrieval Tool] Pruned search space: 500 theoretical pairs -> 220 candidate pairs.",
        "[BioBERT Tool] Semantic evaluation active on fine-tuned weights (biobert_nli_finetuned).",
        "[Clinical Auditor] Completed tri-state audit: 164 HIGH, 25 NEEDS VERIFICATION, 31 EXCLUDED."
      ]
    });
  };

  const selectedTrial = trials.find(t => t.trial_id === selectedTrialId) || trials[0];
  const candidatesForTrial = fleetResults?.by_trial?.[selectedTrialId] || [];

  const filteredCandidates = candidatesForTrial.filter(c => {
    const matchesTier = tierFilter === "ALL" || c.tier === tierFilter;
    const matchesSearch = searchQuery === "" ||
      c.patient_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.patient_name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesTier && matchesSearch;
  });

  const patientOpportunities = fleetResults?.by_patient?.[selectedPatientId] || [];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-teal-500 selection:text-white">
      {/* ==========================================
          HEADER & COMMAND BAR
      ========================================== */}
      <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-teal-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-teal-500/20 text-slate-950 font-black text-xl">
              ⚡
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                  TrialMatch <span className="text-teal-400 font-mono text-sm px-2 py-0.5 rounded border border-teal-500/30 bg-teal-500/10">v2.0 AGENTIC</span>
                </h1>
                <span className="flex h-2.5 w-2.5 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                </span>
              </div>
              <p className="text-xs text-slate-400">Autonomous Population-Scale Clinical Trial Matchmaker & Auditor</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs">
              <span className={`w-2 h-2 rounded-full ${backendConnected ? "bg-emerald-400" : "bg-amber-400"}`}></span>
              <span className="text-slate-300 font-mono">
                {backendConnected ? "Backend Connected (CUDA/CPU)" : "Local Simulation Mode"}
              </span>
            </div>

            <button
              onClick={handleRunFleet}
              disabled={isLoading}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold text-sm transition-all duration-200 shadow-md ${
                isLoading
                  ? "bg-slate-700 text-slate-400 cursor-not-allowed"
                  : "bg-gradient-to-r from-teal-500 to-emerald-600 hover:from-teal-400 hover:to-emerald-500 text-slate-950 shadow-teal-500/20 active:scale-95"
              }`}
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                  <span>Agent Running...</span>
                </>
              ) : (
                <>
                  <span>🚀</span>
                  <span>Run Matchmaker Fleet</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* NAVIGATION TABS */}
        <div className="max-w-7xl mx-auto px-6 flex gap-1 border-t border-slate-800/60">
          {[
            { id: "trial-centric", label: "Trial-Centric View", icon: "🔬" },
            { id: "patient-centric", label: "Patient-Centric View", icon: "👤" },
            { id: "patients", label: `Patient Cohort (${fleetResults?.total_patients || 50})`, icon: "👥" },
            { id: "trials", label: `Active Protocols (${trials.length})`, icon: "📋" }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-3 px-4 font-medium text-xs md:text-sm flex items-center gap-2 border-b-2 transition-all duration-150 ${
                activeTab === tab.id
                  ? "border-teal-400 text-teal-400 bg-teal-500/5 font-semibold"
                  : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/30"
              }`}
            >
              <span>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </header>

      {/* ==========================================
          GLOBAL FLEET KPI METRIC RIBBON
      ========================================== */}
      <section className="bg-slate-900 border-b border-slate-800/80 px-6 py-4">
        <div className="max-w-7xl mx-auto grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-3 flex flex-col justify-between">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Active Trials</span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-black text-white font-mono">{fleetResults?.total_trials || trials.length}</span>
              <span className="text-xs text-slate-500 font-medium">Protocols</span>
            </div>
          </div>

          <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-3 flex flex-col justify-between">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Cohort Size</span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-black text-teal-400 font-mono">{fleetResults?.total_patients || 50}</span>
              <span className="text-xs text-slate-500 font-medium">Patients</span>
            </div>
          </div>

          <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-3 flex flex-col justify-between">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Assessed Pairs</span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-black text-indigo-400 font-mono">{fleetResults?.total_evaluated_pairs || 220}</span>
              <span className="text-xs text-slate-500 font-medium">Pruned 56%</span>
            </div>
          </div>

          <div className="bg-slate-950/60 border border-emerald-900/40 bg-emerald-950/10 rounded-xl p-3 flex flex-col justify-between">
            <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-400">High Match</span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-black text-emerald-400 font-mono">{fleetResults?.high_match_count || 164}</span>
              <span className="text-xs text-emerald-600 font-medium">Verified 🟢</span>
            </div>
          </div>

          <div className="bg-slate-950/60 border border-amber-900/40 bg-amber-950/10 rounded-xl p-3 flex flex-col justify-between">
            <span className="text-[11px] font-bold uppercase tracking-wider text-amber-400">Needs Verif.</span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-black text-amber-400 font-mono">{fleetResults?.verification_needed_count || 25}</span>
              <span className="text-xs text-amber-600 font-medium">Lab Gaps 🟡</span>
            </div>
          </div>

          <div className="bg-slate-950/60 border border-rose-900/40 bg-rose-950/10 rounded-xl p-3 flex flex-col justify-between">
            <span className="text-[11px] font-bold uppercase tracking-wider text-rose-400">Excluded</span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-black text-rose-400 font-mono">{fleetResults?.excluded_count || 31}</span>
              <span className="text-xs text-rose-600 font-medium">Contraindic. 🔴</span>
            </div>
          </div>
        </div>
      </section>

      {/* ==========================================
          LIVE MATCHMAKER THOUGHT CONSOLE
      ========================================== */}
      <section className="bg-slate-900/40 border-b border-slate-800/80 px-6 py-2">
        <div className="max-w-7xl mx-auto">
          <div
            onClick={() => setIsConsoleOpen(!isConsoleOpen)}
            className="flex items-center justify-between cursor-pointer py-1.5 text-xs text-slate-400 hover:text-slate-200"
          >
            <div className="flex items-center gap-2 font-mono">
              <span className="text-teal-400 font-bold">[MATCHMAKER AGENT LOGS]</span>
              <span>{fleetResults?.execution_logs?.length || 4} steps recorded</span>
            </div>
            <span className="text-[11px] font-mono text-slate-500">{isConsoleOpen ? "▲ Hide Console" : "▼ Expand Console"}</span>
          </div>

          {isConsoleOpen && (
            <div className="mt-1 mb-2 p-3 bg-slate-950 rounded-lg border border-slate-800 font-mono text-xs text-slate-300 max-h-36 overflow-y-auto space-y-1 shadow-inner">
              {(fleetResults?.execution_logs || []).map((log, idx) => (
                <div key={idx} className="flex gap-2">
                  <span className="text-slate-600 select-none">{String(idx + 1).padStart(2, "0")}.</span>
                  <span className={log.includes("Complete") ? "text-emerald-400 font-bold" : (log.includes("Stage") ? "text-teal-300" : "text-slate-300")}>
                    {log}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* ==========================================
          MAIN OPERATIONAL BODY
      ========================================== */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-6">

        {/* ----------------------------------------------------
            TAB 1: TRIAL-CENTRIC VIEW
        ---------------------------------------------------- */}
        {activeTab === "trial-centric" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left: Trial Selector Sidebar */}
            <div className="lg:col-span-4 space-y-3">
              <div className="flex items-center justify-between mb-1">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Select Active Protocol</h3>
                <span className="text-xs text-slate-500 font-mono">{trials.length} available</span>
              </div>

              <div className="space-y-2 max-h-[750px] overflow-y-auto pr-1">
                {trials.map(trial => {
                  const isSelected = trial.trial_id === selectedTrialId;
                  const cands = fleetResults?.by_trial?.[trial.trial_id] || [];
                  const highCount = cands.filter(c => c.tier === "HIGH").length;
                  const verifCount = cands.filter(c => c.tier === "NEEDS VERIFICATION").length;

                  return (
                    <div
                      key={trial.trial_id}
                      onClick={() => setSelectedTrialId(trial.trial_id)}
                      className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                        isSelected
                          ? "bg-slate-900 border-teal-500/70 shadow-lg shadow-teal-500/5 ring-1 ring-teal-500/20"
                          : "bg-slate-900/40 border-slate-800 hover:border-slate-700 hover:bg-slate-900/80"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-xs font-bold px-1.5 py-0.5 rounded bg-slate-800 text-teal-400 border border-slate-700">
                              {trial.trial_id}
                            </span>
                            <span className="text-xs text-slate-400 font-semibold">{trial.phase}</span>
                          </div>
                          <h4 className="font-semibold text-slate-100 text-sm mt-1">{trial.name}</h4>
                        </div>
                      </div>

                      <p className="text-xs text-slate-400 mt-1 line-clamp-1">{trial.summary}</p>

                      <div className="flex items-center gap-3 mt-3 pt-2 border-t border-slate-800/80 text-[11px] font-mono">
                        <span className="text-emerald-400 font-semibold">{highCount} High</span>
                        <span className="text-amber-400 font-semibold">{verifCount} Verif.</span>
                        <span className="text-slate-500 ml-auto">{trial.criteria?.length || 5} Criteria</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Right: Candidate Leaderboard */}
            <div className="lg:col-span-8 space-y-4">
              {/* Trial Header Summary Card */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs px-2 py-0.5 rounded bg-teal-500/10 text-teal-400 border border-teal-500/30 font-bold">
                        {selectedTrial?.trial_id}
                      </span>
                      <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        {selectedTrial?.phase}
                      </span>
                      <span className="text-xs text-slate-400 font-mono">• {selectedTrial?.target_condition}</span>
                    </div>
                    <h2 className="text-xl font-bold text-white mt-1">{selectedTrial?.name}</h2>
                    <p className="text-xs text-slate-400 mt-1">{selectedTrial?.summary}</p>
                  </div>
                </div>

                {/* Filter and Search Bar */}
                <div className="flex flex-wrap items-center justify-between gap-3 mt-4 pt-4 border-t border-slate-800 text-xs">
                  <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-lg border border-slate-800">
                    {["ALL", "HIGH", "NEEDS VERIFICATION", "NOT SUITABLE"].map(f => (
                      <button
                        key={f}
                        onClick={() => setTierFilter(f)}
                        className={`px-2.5 py-1 rounded font-medium transition ${
                          tierFilter === f
                            ? "bg-slate-800 text-white shadow-sm font-semibold"
                            : "text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        {f === "ALL" ? "All Candidates" : f}
                      </button>
                    ))}
                  </div>

                  <input
                    type="text"
                    placeholder="Search candidate by name/ID..."
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 placeholder-slate-500 text-xs focus:outline-none focus:border-teal-500"
                  />
                </div>
              </div>

              {/* Candidate Cards Leaderboard */}
              <div className="space-y-3">
                {filteredCandidates.length === 0 ? (
                  <div className="p-8 text-center bg-slate-900/40 rounded-xl border border-slate-800 text-slate-400 text-sm">
                    No candidates match the selected tier filter.
                  </div>
                ) : (
                  filteredCandidates.map(candidate => {
                    const isHigh = candidate.tier === "HIGH";
                    const isVerif = candidate.tier === "NEEDS VERIFICATION";

                    return (
                      <div
                        key={candidate.match_id}
                        className="bg-slate-900 border border-slate-800/90 rounded-xl p-4 hover:border-slate-700 transition flex flex-col justify-between gap-3"
                      >
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-mono text-sm font-bold text-white">{candidate.patient_name}</span>
                              <span className="font-mono text-xs text-slate-400 px-1.5 py-0.5 rounded bg-slate-800">
                                {candidate.patient_id}
                              </span>
                            </div>
                            <p className="text-xs text-slate-300 mt-1 max-w-xl">{candidate.summary}</p>
                          </div>

                          <div className="flex items-center gap-3">
                            <div className="text-right">
                              <div className="text-lg font-black font-mono text-white">
                                {Math.round(candidate.match_score)}%
                              </div>
                              <span className="text-[10px] text-slate-400 uppercase font-semibold">Match Score</span>
                            </div>

                            <span
                              className={`px-3 py-1 rounded-full text-xs font-bold font-mono border ${
                                isHigh
                                  ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                                  : isVerif
                                  ? "bg-amber-500/10 text-amber-400 border-amber-500/30"
                                  : "bg-rose-500/10 text-rose-400 border-rose-500/30"
                              }`}
                            >
                              {candidate.tier}
                            </span>
                          </div>
                        </div>

                        {/* Action items or violations */}
                        {candidate.action_items?.length > 0 && (
                          <div className="flex items-center gap-2 text-xs bg-amber-500/10 border border-amber-500/20 text-amber-300 px-3 py-1.5 rounded-lg">
                            <span>⚠️</span>
                            <span className="font-medium">Action Required: {candidate.action_items[0]}</span>
                          </div>
                        )}

                        <div className="flex items-center justify-between pt-2 border-t border-slate-800/70 text-xs">
                          <div className="flex items-center gap-2 text-slate-400 font-mono text-[11px]">
                            <span>Criteria: {candidate.counts.passed} Passed</span>
                            <span>•</span>
                            <span>{candidate.counts.unknown} Gaps</span>
                            <span>•</span>
                            <span>{candidate.counts.failed} Failed</span>
                          </div>

                          <button
                            onClick={() => setInspectedMatch(candidate)}
                            className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-teal-300 rounded font-semibold text-xs transition flex items-center gap-1.5"
                          >
                            <span>🔍</span>
                            <span>Inspect Evidence & Audit</span>
                          </button>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          </div>
        )}

        {/* ----------------------------------------------------
            TAB 2: PATIENT-CENTRIC VIEW
        ---------------------------------------------------- */}
        {activeTab === "patient-centric" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left: Patient Cohort Selector */}
            <div className="lg:col-span-4 space-y-3">
              <div className="flex items-center justify-between mb-1">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Select Patient</h3>
                <span className="text-xs text-slate-500 font-mono">{patients.length || 50} total</span>
              </div>

              <div className="space-y-2 max-h-[750px] overflow-y-auto pr-1">
                {(patients.length > 0 ? patients : Array.from({ length: 50 }, (_, i) => ({ patient_id: `P${String(i+1).padStart(3, '0')}`, name: `Patient ${i+1}` }))).map(p => {
                  const isSelected = p.patient_id === selectedPatientId;
                  const opps = fleetResults?.by_patient?.[p.patient_id] || [];
                  const highOpps = opps.filter(o => o.tier === "HIGH").length;

                  return (
                    <div
                      key={p.patient_id}
                      onClick={() => setSelectedPatientId(p.patient_id)}
                      className={`p-3 rounded-xl border cursor-pointer transition ${
                        isSelected
                          ? "bg-slate-900 border-teal-500/70 shadow-lg shadow-teal-500/5 ring-1 ring-teal-500/20"
                          : "bg-slate-900/40 border-slate-800 hover:border-slate-700 hover:bg-slate-900/80"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-xs font-bold text-teal-400">{p.patient_id}</span>
                        <span className="text-xs font-semibold text-white">{p.name}</span>
                      </div>
                      <div className="flex items-center justify-between mt-2 pt-1 border-t border-slate-800/80 text-[11px] font-mono text-slate-400">
                        <span>{opps.length} Evaluated</span>
                        <span className="text-emerald-400 font-bold">{highOpps} High Matches</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Right: Patient Trial Opportunities */}
            <div className="lg:col-span-8 space-y-4">
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-teal-500/10 text-teal-400 border border-teal-500/30">
                        {selectedPatientId}
                      </span>
                      <span className="text-slate-400 text-xs">Patient Profile</span>
                    </div>
                    <h2 className="text-xl font-bold text-white mt-1">
                      {patients.find(p => p.patient_id === selectedPatientId)?.name || selectedPatientId}
                    </h2>
                  </div>
                </div>

                {patients.find(p => p.patient_id === selectedPatientId)?.clinical_text && (
                  <p className="mt-3 text-xs text-slate-300 italic p-3 bg-slate-950 rounded-lg border border-slate-800/80">
                    "{patients.find(p => p.patient_id === selectedPatientId).clinical_text}"
                  </p>
                )}
              </div>

              {/* Opportunity Cards */}
              <div className="space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Matched Trial Opportunities ({patientOpportunities.length})
                </h3>

                {patientOpportunities.length === 0 ? (
                  <div className="p-8 text-center bg-slate-900/40 rounded-xl border border-slate-800 text-slate-400 text-sm">
                    No evaluated trial opportunities found for this patient.
                  </div>
                ) : (
                  patientOpportunities.map(opp => (
                    <div
                      key={opp.match_id}
                      className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between gap-3"
                    >
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-xs font-bold px-1.5 py-0.5 rounded bg-slate-800 text-teal-400 border border-slate-700">
                              {opp.trial_id}
                            </span>
                            <span className="font-bold text-sm text-white">{opp.trial_name}</span>
                          </div>
                          <p className="text-xs text-slate-300 mt-1 max-w-xl">{opp.summary}</p>
                        </div>

                        <div className="flex items-center gap-3">
                          <div className="text-right">
                            <div className="text-lg font-black font-mono text-white">{Math.round(opp.match_score)}%</div>
                          </div>
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-bold font-mono border ${
                              opp.tier === "HIGH"
                                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                                : opp.tier === "NEEDS VERIFICATION"
                                ? "bg-amber-500/10 text-amber-400 border-amber-500/30"
                                : "bg-rose-500/10 text-rose-400 border-rose-500/30"
                            }`}
                          >
                            {opp.tier}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center justify-between pt-2 border-t border-slate-800 text-xs">
                        <span className="text-slate-400 text-[11px] font-mono">
                          {opp.counts.passed} Passed / {opp.counts.total} Total Rules
                        </span>

                        <button
                          onClick={() => setInspectedMatch(opp)}
                          className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-teal-300 rounded font-semibold text-xs transition"
                        >
                          Inspect Evidence
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* ----------------------------------------------------
            TAB 3: PATIENT COHORT DIRECTORY
        ---------------------------------------------------- */}
        {activeTab === "patients" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white">Hospital Patient Cohort</h2>
                <p className="text-xs text-slate-400">Enrolled records with unstructured narratives & structured profiles</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {(patients.length > 0 ? patients : Array.from({ length: 50 }, (_, i) => ({ patient_id: `P${String(i+1).padStart(3, '0')}`, name: `Patient ${i+1}`, clinical_text: "Demographic and clinical progress notes..." }))).map(p => (
                <div key={p.patient_id} className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-mono text-xs font-bold text-teal-400">{p.patient_id}</span>
                      <span className="text-xs font-semibold text-white">{p.name}</span>
                    </div>
                    <p className="text-xs text-slate-400 line-clamp-3 italic">"{p.clinical_text}"</p>
                  </div>

                  {p.structured_profile && (
                    <div className="mt-3 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-400">
                      <span>Age: {p.structured_profile.demographics?.age}</span>
                      <span>HbA1c: {p.structured_profile.labs?.HbA1c?.value}%</span>
                      <span>BMI: {p.structured_profile.labs?.BMI?.value}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ----------------------------------------------------
            TAB 4: ACTIVE PROTOCOLS DIRECTORY
        ---------------------------------------------------- */}
        {activeTab === "trials" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white">Active Trial Protocol Registry</h2>
                <p className="text-xs text-slate-400">Deconstructed atomic inclusion and exclusion criteria</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {trials.map(trial => (
                <div key={trial.trial_id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-slate-800 text-teal-400 border border-slate-700">
                          {trial.trial_id}
                        </span>
                        <span className="text-xs font-semibold text-slate-300">{trial.phase}</span>
                      </div>
                      <h3 className="text-base font-bold text-white mt-1">{trial.name}</h3>
                    </div>
                  </div>

                  <p className="text-xs text-slate-400">{trial.summary}</p>

                  <div className="space-y-1.5 pt-2 border-t border-slate-800">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Atomic Rules:</span>
                    <ul className="space-y-1 text-xs text-slate-300">
                      {trial.criteria?.map(c => (
                        <li key={c.id} className="flex items-start gap-1.5">
                          <span className={`text-[10px] font-bold px-1 rounded uppercase font-mono ${c.clause === "inclusion" ? "text-blue-400 bg-blue-950/60" : "text-rose-400 bg-rose-950/60"}`}>
                            {c.clause === "inclusion" ? "INC" : "EXC"}
                          </span>
                          <span className="text-slate-300">{c.description}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* ==========================================
          EXPLAINABLE EVIDENCE & AUDIT DRAWER (MODAL)
      ========================================== */}
      {inspectedMatch && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 w-full max-w-3xl rounded-2xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden animate-fadeIn">
            {/* Modal Header */}
            <div className="p-6 border-b border-slate-800 flex items-start justify-between bg-slate-950/50">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs px-2 py-0.5 rounded bg-teal-500/10 text-teal-400 border border-teal-500/30 font-bold">
                    {inspectedMatch.trial_id}
                  </span>
                  <span className="font-mono text-xs text-slate-400">↔</span>
                  <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-bold">
                    {inspectedMatch.patient_id}
                  </span>
                  <span
                    className={`ml-2 px-2.5 py-0.5 rounded-full text-xs font-bold font-mono border ${
                      inspectedMatch.tier === "HIGH"
                        ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                        : inspectedMatch.tier === "NEEDS VERIFICATION"
                        ? "bg-amber-500/10 text-amber-400 border-amber-500/30"
                        : "bg-rose-500/10 text-rose-400 border-rose-500/30"
                    }`}
                  >
                    {inspectedMatch.tier} ({Math.round(inspectedMatch.match_score)}%)
                  </span>
                </div>
                <h3 className="text-lg font-bold text-white mt-1">
                  {inspectedMatch.patient_name} — {inspectedMatch.trial_name}
                </h3>
              </div>

              <button
                onClick={() => setInspectedMatch(null)}
                className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center font-bold"
              >
                ✕
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-5 text-xs">
              {/* Verdict Summary */}
              <div className="p-3.5 bg-slate-950 rounded-xl border border-slate-800">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Clinical Auditor Verdict:</span>
                <p className="text-slate-200 mt-1 leading-relaxed">{inspectedMatch.summary}</p>
              </div>

              {/* Action Required Alert */}
              {inspectedMatch.action_items?.length > 0 && (
                <div className="p-3.5 bg-amber-950/20 border border-amber-500/30 rounded-xl text-amber-200 space-y-1">
                  <div className="flex items-center gap-2 font-bold text-amber-400 text-xs uppercase tracking-wide">
                    <span>⚠️</span>
                    <span>Action Required Prior to Enrollment</span>
                  </div>
                  <ul className="list-disc list-inside text-xs space-y-0.5 text-amber-200/90 pl-1">
                    {inspectedMatch.action_items.map((act, i) => (
                      <li key={i}>{act}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Atomic Criteria Evidence Breakdown */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Atomic Criteria Evidence Trace ({inspectedMatch.criteria_evaluations?.length || 0})
                </h4>

                <div className="space-y-2.5">
                  {inspectedMatch.criteria_evaluations?.map((ev, i) => {
                    const isPass = ev.status === "PASS";
                    const isFail = ev.status === "FAIL";

                    return (
                      <div
                        key={i}
                        className={`p-3.5 rounded-xl border ${
                          isPass
                            ? "bg-slate-950/60 border-slate-800"
                            : isFail
                            ? "bg-rose-950/10 border-rose-900/40"
                            : "bg-amber-950/10 border-amber-900/40"
                        }`}
                      >
                        <div className="flex items-center justify-between gap-2 mb-1.5">
                          <div className="flex items-center gap-2">
                            <span
                              className={`text-[10px] font-bold px-1.5 py-0.5 rounded font-mono uppercase ${
                                ev.clause === "inclusion" ? "text-blue-400 bg-blue-950/80" : "text-purple-400 bg-purple-950/80"
                              }`}
                            >
                              {ev.clause}
                            </span>
                            <span className="font-semibold text-slate-200 text-xs">{ev.rule_description}</span>
                          </div>

                          <div className="flex items-center gap-2">
                            <span
                              className={`px-2 py-0.5 rounded text-[11px] font-mono font-bold ${
                                isPass
                                  ? "bg-emerald-500/20 text-emerald-400"
                                  : isFail
                                  ? "bg-rose-500/20 text-rose-400"
                                  : "bg-amber-500/20 text-amber-400"
                              }`}
                            >
                              {ev.status}
                            </span>
                          </div>
                        </div>

                        {/* Quoted Evidence */}
                        <div className="p-2.5 bg-slate-900/80 rounded-lg border border-slate-800/80 mt-2 text-xs">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1">
                            Extracted EHR Evidence:
                          </span>
                          <p className="text-slate-300 font-mono text-[11px] leading-relaxed">
                            {ev.evidence_quote}
                          </p>
                        </div>

                        {/* Tool Attribution */}
                        <div className="flex items-center justify-between mt-2 text-[10px] text-slate-400 font-mono">
                          <span>Tool: <strong className="text-teal-400">{ev.tool_used}</strong></span>
                          <span>Confidence: <strong>{Math.round((ev.confidence || 1.0) * 100)}%</strong></span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-slate-800 bg-slate-950/50 flex justify-end">
              <button
                onClick={() => setInspectedMatch(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold transition"
              >
                Close Audit Inspection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}