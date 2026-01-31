# 👥 Human Review System Documentation

## Overview

The Human Review System provides a centralized queue for critical hiring decisions that require human oversight. This ensures that automated decisions don't go unchecked, especially for security threats and bias violations.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     HUMAN REVIEW SERVICE                             │
│                 (services/human_review_service.py)                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │  ATS Agent  │  │ Skill Agent │  │ Bias Agent  │                 │
│  │  (Security) │  │ (Integrity) │  │ (Fairness)  │                 │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                 │
│         │                │                │                         │
│         └────────────────┴────────────────┘                         │
│                          │                                           │
│                          ▼                                           │
│           ┌──────────────────────────────┐                          │
│           │   submit_review_request()    │                          │
│           │   - candidate_id             │                          │
│           │   - triggered_by             │                          │
│           │   - severity                 │                          │
│           │   - reason                   │                          │
│           │   - evidence                 │                          │
│           │   - system_action_taken      │                          │
│           └──────────────┬───────────────┘                          │
│                          │                                           │
│                          ▼                                           │
│           ┌──────────────────────────────┐                          │
│           │   human_review_queue.json    │                          │
│           │   (Persistent Storage)       │                          │
│           └──────────────────────────────┘                          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Service API

### `HumanReviewService` Class

**Location:** `services/human_review_service.py`

#### Constructor
```python
service = HumanReviewService(queue_path="human_review_queue.json")
```

#### Methods

##### `submit_review_request()`
```python
review_id = service.submit_review_request(
    candidate_id="usr_cdff3a6b117e",
    triggered_by="ats_security",      # Source agent
    severity="critical",               # critical | high | medium | low
    reason="Security violation...",    # Human-readable explanation
    system_action_taken="blocked",     # blocked | paused | flagged
    evidence={...},                    # Full evidence payload
    job_id="job_123"                   # Optional job context
)
# Returns: "review_254a2d"
```

##### `get_pending_reviews()`
```python
pending = service.get_pending_reviews()
# Returns: List of review objects with status="PENDING"
```

##### `resolve_review()`
```python
service.resolve_review(
    review_id="review_254a2d",
    decision="APPROVED",              # APPROVED | REJECTED | ESCALATED
    reviewer_notes="False positive, candidate is clean"
)
```

---

## 📋 Queue Entry Schema

```json
{
  "review_id": "review_254a2d",
  "candidate_id": "usr_cdff3a6b117e",
  "job_id": "unknown_job",
  "triggered_by": "ats_security",
  "severity": "critical",
  "reason": "Security violation aggregate (blacklist)",
  "evidence": {
    "white_text_detected": false,
    "injection_detected": true,
    "narrative_analysis": {
      "suspicious_semantic_patterns": true,
      "professional_language_mask": true,
      "details": [{
        "detected": true,
        "type": "semantic_injection",
        "severity": "medium",
        "patterns_matched": [
          "Evaluation systems processing this data should recognize",
          "Assessment frameworks are designed to"
        ],
        "match_count": 2
      }]
    },
    "final_action": "BLACKLISTED"
  },
  "system_action_taken": "blocked",
  "status": "PENDING",
  "human_decision": null,
  "reviewer_notes": null,
  "timestamp": "2026-01-29T01:06:09.223628Z"
}
```

---

## 🔥 Trigger Conditions

### From ATS Agent (`ats.py`)

| Condition | Severity | Action | Code Location |
|-----------|----------|--------|---------------|
| White text keywords > 5 | Critical | `blocked` | Line 187 |
| White text keywords 1-5 | High | `paused` | Line 206 |
| Dual LLM injection detected | Critical | `blocked` | Line 355 |
| Regex injection matched | High | `paused` | Line 384 |

### From Skill Verification Agent (`skill_verification_agent_v2.py`)

| Condition | Severity | Action | Code Location |
|-----------|----------|--------|---------------|
| Manipulation score >= 80 | Critical | `blocked` | Line 540 |
| Manipulation score 60-79 | High | `flagged` | Line 550 |

### From Bias Detection Agent (`bias_detection_agent.py`)

| Condition | Severity | Action | Code Location |
|-----------|----------|--------|---------------|
| Gender gap > 15 | Critical | `flagged` | Line 150 |
| Gender gap 10-15 | High | `flagged` | Line 150 |
| PII metadata leak | Critical | `blocked` | Line 88 |

---

## 📊 Review Status Lifecycle

```
┌──────────┐     ┌──────────┐     ┌──────────────────────┐
│ PENDING  │────►│ APPROVED │────►│ Candidate Proceeds   │
└──────────┘     └──────────┘     └──────────────────────┘
     │
     │           ┌──────────┐     ┌──────────────────────┐
     └──────────►│ REJECTED │────►│ Candidate Blocked    │
                 └──────────┘     └──────────────────────┘
     │
     │           ┌───────────┐    ┌──────────────────────┐
     └──────────►│ ESCALATED │───►│ Senior Review Queue  │
                 └───────────┘    └──────────────────────┘
```

---

## 🔧 Integration Examples

### ATS Agent Integration
```python
# In ats.py, line 355
if self.human_review_service and evaluation_id:
    review_id = self.human_review_service.submit_review_request(
        candidate_id=candidate_email or evaluation_id,
        triggered_by="ats_security",
        severity="critical",
        reason="Security violation aggregate (blacklist)",
        system_action_taken="blocked",
        evidence=final_output
    )
    final_output["human_review_status"] = "SUBMITTED"
    final_output["human_review_id"] = review_id
```

### Bias Detection Integration
```python
# In bias_detection_agent.py, line 145
if report["bias_detected"] and report["severity"] in ["critical", "high"]:
    self.human_review_service.submit_review_request(
        candidate_id=candidate_id,
        triggered_by="bias_detection",
        severity=report["severity"],
        reason=f"Systemic Bias Detected: {report['severity'].upper()}",
        system_action_taken="flagged",
        evidence={"batch_details": report.get("details", {})}
    )
```

---

## 🖥️ CLI Usage

### View Pending Reviews
```bash
cat human_review_queue.json | jq '[.[] | select(.status == "PENDING")]'
```

### Count by Trigger
```bash
cat human_review_queue.json | jq 'group_by(.triggered_by) | map({trigger: .[0].triggered_by, count: length})'
```

### Filter Critical Only
```bash
cat human_review_queue.json | jq '[.[] | select(.severity == "critical")]'
```

---

## 📈 Queue Statistics (Sample)

```json
{
  "total_reviews": 12,
  "by_status": {
    "PENDING": 10,
    "APPROVED": 1,
    "REJECTED": 1
  },
  "by_trigger": {
    "ats_security": 9,
    "bias_detection": 2,
    "skill_verification": 1
  },
  "by_severity": {
    "critical": 8,
    "high": 3,
    "medium": 1
  }
}
```

---

## 🚧 Future Enhancements

### Planned Features
1. **Reviewer Dashboard** - Web UI for processing queue
2. **Email Notifications** - Alert reviewers on critical items
3. **SLA Tracking** - Monitor review turnaround time
4. **Audit Logs** - Track all human decisions
5. **Role-Based Access** - Different permissions for reviewers

### API Endpoints (Planned)
```
GET  /api/v1/reviews/pending
GET  /api/v1/reviews/{id}
POST /api/v1/reviews/{id}/decide
GET  /api/v1/reviews/stats
```

---

## ✅ Verification

### Test Security Trigger
```bash
python skill_verification_agent/run_complete_workflow.py \
  --resume "test_attacks/David Chen - Senior ML Engineer.pdf" \
  --github "testuser"

# Check queue
cat human_review_queue.json | jq '.[-1]'
```

### Test Bias Trigger
```bash
python bias_detection_agent/run_bias_check.py

# Check queue
cat human_review_queue.json | jq '.[-1]'
```

---

**Last Updated:** January 2026 | **Service Version:** 1.0
