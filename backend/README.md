# Backend – Fair Hiring Platform

FastAPI backend responsible for:
- Authentication
- [x] Debug Skill Agent connectivity
    - [x] Identify Skill Agent service script
    - [x] Start Skill Agent service (Advised user)
    - [x] Verify connectivity with backend

---

## 🚀 Run Backend

```bash
venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000
```

Health:
```
GET /health
```

---

## 🔐 Authentication

### Candidate

**Signup**
```
POST /auth/candidate/signup
```

**Login**
```
POST /auth/candidate/login
```

Returns:
- `candidate_id`
- `anon_id` (persistent, privacy-safe)

### Company

**Signup**
```
POST /auth/company/signup
```

**Login**
```
POST /auth/company/login
```

---

## 📄 Core APIs

### Jobs

```
POST /company/job
GET /candidate/jobs
GET /company/{company_id}/jobs
```

### Applications

```
POST /candidate/apply
GET /candidate/{anon_id}/applications
```

### Matching

```
POST /company/{company_id}/jobs/{job_id}/run-matching
GET /company/{company_id}/jobs/{job_id}/selected
```

### Stats

```
GET /company/{company_id}/stats
GET /candidate/{anon_id}/stats
```

### Passport

```
GET /passport/{anon_id}
```

---

## 🧠 Agents Integration

Backend calls agents synchronously:

```
Skill → Bias → Matching
```

All results are persisted in:
- `credentials`
- `agent_runs`
- `applications`

---

## 🗄 Database

**PostgreSQL database:** `fairhire`

Key tables:
- `candidates`
- `companies`
- `jobs`
- `applications`
- `credentials`
- `agent_runs`

---

## ✅ Status

- Strict validation (no auto-creation bugs)
- Transparent error handling
- Full observability via logs
