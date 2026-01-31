# Bias Detection Agent

**Role:** The Auditor
**Version:** V2 (Batch Statistical Analysis)

## 🎯 Purpose
The `BiasDetectionAgent` ensures the hiring pipeline remains fair. It performs a **statistical audit** on recent "batch" history to detect systemic anomalies in scoring based on protected attributes (Gender, College Tier) or platform bias (GitHub Account Age).

## 🧠 Key Capabilities
1.  **Read-Only Observation**: The agent *never* alters a candidate's score. It only "Observe and Report".
2.  **Batch Analysis**: Detects patterns (e.g., "Females consistently scoring lower than Males despite similar portfolios").
3.  **Mock Data Simulation**: Capable of loading historical mock data to test detection logic.

## 📥 Inputs
- **Candidate Credential**: The verified skills object.
- **Historical Data**: Batch history (Simulated/DB).

## 📤 Output (`bias_report.json`)
```json
{
  "bias_detected": true,
  "bias_scope": "systemic",
  "candidate_impact": "none",
  "action": "proceed_to_matching",
  "details": {
    "gender_gap": 8.68
  }
}
```

## 🛠️ Usage

### Run Individually
```bash
# From project root
python bias_detection_agent/agents/bias_detection_agent.py
```
This will generate `bias_report.json` based on the current `final_credential.json` and internal mock history.
