# Transparent Matching Agent

**Role:** The Recruiter
**Version:** V1 (Honest Matching)

## 🎯 Purpose
The `MatchingAgent` compares the verified candidate credential against a specific Job Description (JD). Unlike traditional ATS, it uses **Honest Matching Logic**, which prioritizes core requirements over fuzzy "match percentages".

## 🧠 Key Logic
1.  **Core vs Frameworks**: Matches are weighted (Core Skills > Frameworks).
2.  **Conditional Matching**:
    - If a candidate has a high score but is missing a **Core Skill** (e.g., System Design), the status is `CONDITIONAL_MATCH`.
    - This prevents auto-rejection while flagging the specific gap.
3.  **Bias Transparency**: It accepts the `bias_report.json` and updates the output context to inform the human reviewer if the system is currently under audit.

## 📥 Inputs
- **Credential**: `final_credential.json`
- **Bias Report**: `bias_report.json`
- **Job Description**: `mock_job_description.json`

## 📤 Output (`match_result.json`)
```json
{
  "match_status": "CONDITIONAL_MATCH",
  "match_score": 70,
  "decision_reason": "Missing core requirement: System Design",
  "bias_context": {
    "status": "monitored",
    "bias_scope": "system_level"
  }
}
```

## 🛠️ Usage

### Run Individually
```bash
# From project root
python matching_agent/agents/matching_agent.py
```
