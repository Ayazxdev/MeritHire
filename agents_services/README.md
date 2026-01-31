# Agent Services – Fair Hiring Platform

Independent microservices used by the backend.

---

## 🧠 Available Agents

### Skill Verification Agent (8001)

- Extracts skills from resume + profiles
- Outputs confidence score

### Bias Detection Agent (8002)

- Checks gender & college bias
- Determines fairness eligibility

### Matching Agent (8003)

- Scores candidates vs job description

---

## 🚀 Start All Agents

```bash
backend\venv\Scripts\python.exe start_all.py
```

Health checks:

```
GET /health
```

---

## 🔄 How They're Used

- Backend controls invocation
- Agents are stateless
- Results persisted by backend

---

## ⚠ Notes

- Agents must be running before applications
- Backend will fail gracefully if agents are unavailable
