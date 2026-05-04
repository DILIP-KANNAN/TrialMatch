import React, { useState } from "react";

// Sample data for demo
const samplePatients = [
  {
    id: 1,
    report_text: "Mr. Davis is a 45-year-old male presenting with Type 2 Diabetes. His recent labs show an HbA1c of 7.5. He has a BMI of 32. He has no history of insulin therapy. Past medical history is significant for Hypertension."
  },
  {
    id: 2,
    report_text: "Patient is a 52-year-old female with Type 2 Diabetes. Her HbA1c is currently 8.2 and her BMI is 28. She has not been on insulin therapy. She also suffers from chronic Kidney Disease."
  }
];

const sampleTrials = [
  {
    trial_id: "T1",
    name: "DIAMOND Study",
    condition: "Type 2 Diabetes",
    inclusion: ["Age between 40 and 65", "HbA1c > 7.0", "No insulin therapy"],
    exclusion: ["Kidney disease", "Heart failure"]
  },
  {
    trial_id: "T2",
    name: "MetaControl Trial",
    condition: "Type 2 Diabetes",
    inclusion: ["Age 30-60", "HbA1c between 6.5-9", "BMI > 25"],
    exclusion: ["Pregnancy", "Active infection"]
  }
];

function TrialMatch() {
  const [activeTab, setActiveTab] = useState("patients");
  const [patients, setPatients] = useState(samplePatients);
  const [trials, setTrials] = useState(sampleTrials);

  const [patientForm, setPatientForm] = useState({
    report_text: ""
  });

  const [trialForm, setTrialForm] = useState({
    trial_id: "",
    name: "",
    condition: "Type 2 Diabetes",
    inclusion: "",
    exclusion: ""
  });

  const [selectedPatient, setSelectedPatient] = useState(null);
  const [selectedTrial, setSelectedTrial] = useState(null);
  const [matchResults, setMatchResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Add Patient
  const handleAddPatient = () => {
    if (!patientForm.report_text) {
      alert("Please enter the patient's clinical notes");
      return;
    }

    const newPatient = {
      id: Math.max(...patients.map(p => p.id), 0) + 1,
      report_text: patientForm.report_text
    };

    setPatients([...patients, newPatient]);
    setPatientForm({
      report_text: ""
    });
  };

  // Add Trial
  const handleAddTrial = () => {
    if (!trialForm.trial_id || !trialForm.name || !trialForm.inclusion || !trialForm.exclusion) {
      alert("Please fill in all required fields");
      return;
    }

    const newTrial = {
      trial_id: trialForm.trial_id,
      name: trialForm.name,
      condition: trialForm.condition,
      inclusion: trialForm.inclusion.split("\n").filter(i => i.trim()),
      exclusion: trialForm.exclusion.split("\n").filter(e => e.trim())
    };

    setTrials([...trials, newTrial]);
    setTrialForm({
      trial_id: "",
      name: "",
      condition: "Type 2 Diabetes",
      inclusion: "",
      exclusion: ""
    });
  };

  // Backend matching function
  const handleMatch = async () => {
    if (!selectedPatient || !selectedTrial) {
      alert("Please select both a patient and a trial");
      return;
    }

    setIsLoading(true);

    const patientText = selectedPatient.report_text;

    try {
      const response = await fetch("http://127.0.0.1:5000/match", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          patient_text: patientText, 
          inclusion_criteria: selectedTrial.inclusion,
          exclusion_criteria: selectedTrial.exclusion,
          trial_name: selectedTrial.name
        })
      });

      if (!response.ok) {
        throw new Error("Failed to match. Backend returned an error.");
      }

      const data = await response.json();

      setMatchResults({
        patient: selectedPatient,
        trial: selectedTrial,
        eligible: data.final_score > 0.6,
        score: Math.round(data.final_score * 100),
        satisfiedConditions: data.explanation.criteria_analysis.satisfied_conditions,
        failedConditions: data.explanation.criteria_analysis.failed_conditions,
        semanticAnalysis: data.explanation.semantic_analysis,
        interpretation: data.explanation.interpretation,
        bertScore: data.bert_score,
        ruleScore: data.rule_score
      });
    } catch (error) {
      console.error(error);
      alert("Error matching patient and trial: " + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* HEADER */}
      <header className="bg-gradient-to-r from-teal-700 to-teal-600 text-white shadow-lg sticky top-0 z-100">
        <div className="max-w-7xl mx-auto px-6 py-8 flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold tracking-tight">TrialMatch</h1>
            <p className="text-teal-100 mt-1 text-sm font-light">Smart Clinical Trial Matching</p>
          </div>
          <div className="w-16 h-16 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" strokeWidth="2" />
              <path d="M12 6v6l4 2" strokeWidth="2" />
            </svg>
          </div>
        </div>
      </header>

      {/* NAVIGATION */}
      <nav className="bg-white border-b border-gray-200 sticky top-20 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 flex gap-8">
          <button
            onClick={() => setActiveTab("patients")}
            className={`py-4 px-1 border-b-4 font-medium text-sm transition-colors ${
              activeTab === "patients"
                ? "border-teal-600 text-teal-600"
                : "border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300"
            }`}
          >
            <span className="mr-2">👥</span>Patients
          </button>
          <button
            onClick={() => setActiveTab("trials")}
            className={`py-4 px-1 border-b-4 font-medium text-sm transition-colors ${
              activeTab === "trials"
                ? "border-teal-600 text-teal-600"
                : "border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300"
            }`}
          >
            <span className="mr-2">🔬</span>Clinical Trials
          </button>
          <button
            onClick={() => setActiveTab("match")}
            className={`py-4 px-1 border-b-4 font-medium text-sm transition-colors ${
              activeTab === "match"
                ? "border-teal-600 text-teal-600"
                : "border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300"
            }`}
          >
            <span className="mr-2">⚡</span>Match Patients
          </button>
        </div>
      </nav>

      {/* MAIN CONTENT */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
        {/* PATIENTS TAB */}
        {activeTab === "patients" && (
          <div className="space-y-6 animate-fadeIn">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">Patient Registry</h2>
              <p className="text-gray-600 mt-2">Add and manage patient information for trial matching</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Patient Form */}
              <div className="bg-white rounded-xl shadow border border-gray-200 p-8 flex flex-col h-full">
                <h3 className="text-xl font-semibold text-gray-900 mb-6">Add New Patient</h3>
                <div className="space-y-5 flex-1 flex flex-col">
                  <div className="flex-1 flex flex-col">
                    <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">Clinical Notes / Report *</label>
                    <textarea
                      placeholder="Paste the unstructured patient report or clinical notes here..."
                      value={patientForm.report_text}
                      onChange={(e) => setPatientForm({ report_text: e.target.value })}
                      className="w-full flex-1 min-h-[250px] px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition resize-none"
                    />
                  </div>

                  <button
                    onClick={handleAddPatient}
                    className="w-full bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-700 hover:to-teal-600 text-white font-semibold py-3 rounded-lg transition transform hover:-translate-y-0.5 active:translate-y-0 shadow-md mt-auto"
                  >
                    + Add Patient
                  </button>
                </div>
              </div>

              {/* Patients List */}
              <div className="bg-white rounded-xl shadow border border-gray-200 p-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-6">Patient List ({patients.length})</h3>
                <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
                  {patients.map((patient) => (
                    <div
                      key={patient.id}
                      onClick={() => setSelectedPatient(patient)}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition ${
                        selectedPatient?.id === patient.id
                          ? "border-teal-600 bg-teal-50"
                          : "border-gray-200 hover:border-teal-400 hover:shadow"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-sm font-bold text-teal-600">ID #{patient.id}</span>
                        <span className="text-xs font-semibold bg-gray-100 text-gray-700 px-3 py-1 rounded-full">
                          Unstructured
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 line-clamp-3">
                        {patient.report_text}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TRIALS TAB */}
        {activeTab === "trials" && (
          <div className="space-y-6 animate-fadeIn">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">Clinical Trials</h2>
              <p className="text-gray-600 mt-2">Manage trial criteria and requirements</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Trial Form */}
              <div className="bg-white rounded-xl shadow border border-gray-200 p-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-6">Add New Trial</h3>
                <div className="space-y-5">
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">Trial ID *</label>
                    <input
                      type="text"
                      placeholder="e.g., T1"
                      value={trialForm.trial_id}
                      onChange={(e) => setTrialForm({ ...trialForm, trial_id: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">Trial Name *</label>
                    <input
                      type="text"
                      placeholder="e.g., DIAMOND Study"
                      value={trialForm.name}
                      onChange={(e) => setTrialForm({ ...trialForm, name: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">Condition</label>
                    <select
                      value={trialForm.condition}
                      onChange={(e) => setTrialForm({ ...trialForm, condition: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition"
                    >
                      <option>Type 2 Diabetes</option>
                      <option>Type 1 Diabetes</option>
                      <option>Hypertension</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">Inclusion Criteria *</label>
                    <textarea
                      placeholder="One criterion per line"
                      value={trialForm.inclusion}
                      onChange={(e) => setTrialForm({ ...trialForm, inclusion: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition resize-vertical"
                      rows="4"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">Exclusion Criteria *</label>
                    <textarea
                      placeholder="One criterion per line"
                      value={trialForm.exclusion}
                      onChange={(e) => setTrialForm({ ...trialForm, exclusion: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition resize-vertical"
                      rows="4"
                    />
                  </div>

                  <button
                    onClick={handleAddTrial}
                    className="w-full bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-700 hover:to-teal-600 text-white font-semibold py-3 rounded-lg transition transform hover:-translate-y-0.5 active:translate-y-0 shadow-md"
                  >
                    + Add Trial
                  </button>
                </div>
              </div>

              {/* Trials List */}
              <div className="bg-white rounded-xl shadow border border-gray-200 p-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-6">Trial List ({trials.length})</h3>
                <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
                  {trials.map((trial) => (
                    <div
                      key={trial.trial_id}
                      onClick={() => setSelectedTrial(trial)}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition ${
                        selectedTrial?.trial_id === trial.trial_id
                          ? "border-teal-600 bg-teal-50"
                          : "border-gray-200 hover:border-teal-400 hover:shadow"
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-semibold text-gray-900">{trial.name}</h4>
                        <span className="text-xs font-bold bg-teal-600 text-white px-2 py-1 rounded">
                          {trial.trial_id}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="font-semibold text-gray-700 mb-1">✓ Inclusion ({trial.inclusion.length})</p>
                          <ul className="text-xs text-gray-600 space-y-0.5">
                            {trial.inclusion.slice(0, 2).map((c, i) => (
                              <li key={i}>• {c}</li>
                            ))}
                            {trial.inclusion.length > 2 && (
                              <li className="text-teal-600 font-semibold">+{trial.inclusion.length - 2} more</li>
                            )}
                          </ul>
                        </div>
                        <div>
                          <p className="font-semibold text-gray-700 mb-1">✗ Exclusion ({trial.exclusion.length})</p>
                          <ul className="text-xs text-gray-600 space-y-0.5">
                            {trial.exclusion.slice(0, 2).map((c, i) => (
                              <li key={i}>• {c}</li>
                            ))}
                            {trial.exclusion.length > 2 && (
                              <li className="text-teal-600 font-semibold">+{trial.exclusion.length - 2} more</li>
                            )}
                          </ul>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* MATCHING TAB */}
        {activeTab === "match" && (
          <div className="space-y-6 animate-fadeIn">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">Patient-Trial Matching</h2>
              <p className="text-gray-600 mt-2">Select a patient and trial to evaluate eligibility</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Selection Panel */}
              <div className="bg-white rounded-xl shadow border border-gray-200 p-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-6">Select Patient & Trial</h3>
                <div className="space-y-5">
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">Choose Patient</label>
                    <select
                      value={selectedPatient?.id || ""}
                      onChange={(e) => {
                        const patient = patients.find(p => p.id === parseInt(e.target.value));
                        setSelectedPatient(patient);
                      }}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition"
                    >
                      <option value="">-- Select a patient --</option>
                      {patients.map((p) => (
                        <option key={p.id} value={p.id}>
                          Patient #{p.id}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">Choose Trial</label>
                    <select
                      value={selectedTrial?.trial_id || ""}
                      onChange={(e) => {
                        const trial = trials.find(t => t.trial_id === e.target.value);
                        setSelectedTrial(trial);
                      }}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition"
                    >
                      <option value="">-- Select a trial --</option>
                      {trials.map((t) => (
                        <option key={t.trial_id} value={t.trial_id}>
                          {t.name} ({t.trial_id})
                        </option>
                      ))}
                    </select>
                  </div>

                  <button
                    onClick={handleMatch}
                    disabled={isLoading}
                    className={`w-full text-white font-semibold py-3 rounded-lg transition transform shadow-md text-lg ${isLoading ? 'bg-gray-400 cursor-not-allowed' : 'bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-700 hover:to-teal-600 hover:-translate-y-0.5 active:translate-y-0'}`}
                  >
                    {isLoading ? "Analyzing via BioBERT..." : "Analyze Eligibility"}
                  </button>
                </div>

                {selectedPatient && (
                  <div className="mt-6 p-4 bg-gray-50 rounded-lg border-l-4 border-teal-600">
                    <h4 className="font-semibold text-gray-900 mb-3">Selected Patient</h4>
                    <div className="mt-3">
                      <p className="text-sm text-gray-700 italic border-l-2 border-gray-300 pl-3">"{selectedPatient.report_text}"</p>
                    </div>
                  </div>
                )}

                {selectedTrial && (
                  <div className="mt-4 p-4 bg-gray-50 rounded-lg border-l-4 border-teal-600">
                    <h4 className="font-semibold text-gray-900 mb-2">Selected Trial</h4>
                    <p className="font-semibold text-gray-900">{selectedTrial.name}</p>
                    <p className="text-sm text-gray-600">{selectedTrial.trial_id}</p>
                  </div>
                )}
              </div>

              {/* Results Panel */}
              <div className="bg-white rounded-xl shadow border border-gray-200 p-8">
                {matchResults ? (
                  <div className="space-y-6">
                    <div
                      className={`p-6 rounded-lg border-2 ${
                        matchResults.eligible
                          ? "bg-green-50 border-green-300"
                          : "bg-red-50 border-red-300"
                      }`}
                    >
                      <div className="flex items-center gap-4">
                        <div
                          className={`w-16 h-16 rounded-full flex items-center justify-center text-3xl font-bold ${
                            matchResults.eligible
                              ? "bg-green-200 text-green-700"
                              : "bg-red-200 text-red-700"
                          }`}
                        >
                          {matchResults.eligible ? "✓" : "✗"}
                        </div>
                        <div>
                          <h3 className={`text-2xl font-bold ${
                            matchResults.eligible ? "text-green-700" : "text-red-700"
                          }`}>
                            {matchResults.eligible ? "Eligible" : "Not Eligible"}
                          </h3>
                          <p className="text-gray-700 mt-1">
                            Match Score: <span className="font-bold text-lg">{matchResults.score}%</span>
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      {matchResults.satisfiedConditions.length > 0 && (
                        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                          <h4 className="font-semibold text-green-700 mb-3">✓ Satisfied Criteria</h4>
                          <ul className="space-y-2">
                            {matchResults.satisfiedConditions.map((c, i) => (
                              <li key={i} className="text-sm text-green-700 flex gap-2">
                                <span className="font-bold">•</span>
                                <span>{c}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {matchResults.failedConditions.length > 0 && (
                        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                          <h4 className="font-semibold text-red-700 mb-3">✗ Failed Criteria</h4>
                          <ul className="space-y-2">
                            {matchResults.failedConditions.map((c, i) => (
                              <li key={i} className="text-sm text-red-700 flex gap-2">
                                <span className="font-bold">•</span>
                                <span>{c}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                    
                    {/* BioBERT Semantic Analysis */}
                    <div className="mt-6 p-5 bg-teal-50 border border-teal-200 rounded-lg shadow-inner">
                      <div className="flex items-center gap-3 mb-4">
                        <span className="text-2xl">🧠</span>
                        <h4 className="font-bold text-teal-800 text-lg">BioBERT Semantic Analysis</h4>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="bg-white p-3 rounded shadow-sm border border-teal-100">
                          <p className="text-xs text-teal-600 uppercase font-bold">Rule-Based Score</p>
                          <p className="text-xl font-bold text-gray-800">{Math.round(matchResults.ruleScore * 100)}%</p>
                        </div>
                        <div className="bg-white p-3 rounded shadow-sm border border-teal-100">
                          <p className="text-xs text-teal-600 uppercase font-bold">Semantic Score</p>
                          <p className="text-xl font-bold text-gray-800">{Math.round(matchResults.bertScore * 100)}%</p>
                        </div>
                      </div>
                      
                      <div className="bg-white p-4 rounded shadow-sm border border-teal-100 mb-4">
                        <h5 className="text-sm font-bold text-gray-800 mb-2">Interpretation</h5>
                        <p className="text-sm text-gray-700">{matchResults.interpretation}</p>
                      </div>
                      
                      <p className="text-sm text-teal-700 italic">
                        "{matchResults.semanticAnalysis}"
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-12 text-center">
                    <div className="text-5xl mb-4">🔍</div>
                    <p className="text-gray-600">
                      Select a patient and trial, then click "Analyze Eligibility" to see matching results.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default TrialMatch;