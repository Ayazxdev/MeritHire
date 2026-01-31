# Fair Hiring Platform (End-to-End System)

A full-stack, agent-assisted hiring platform that enables **fair, explainable, and data-driven recruitment**.

This repository contains the **complete production-style system**:

- Real authentication (candidate + company)
- Job creation and applications
- Skill verification, bias detection, and matching agents
- Live dashboards powered entirely by the database


Every number you see in the UI is backed by real database state.

---

## 🧠 System Overview

### Core Actors

**Candidates**

- Sign up & log in
- Receive a persistent anonymous ID (`anon_id`)
- Apply to jobs
- View application status, feedback, and skill passport

**Companies**

- Sign up & log in
- Create job roles
- View candidate pipelines
- Run matching to select candidates

### Intelligent Agents

**Skill Verification Agent**  
Extracts skills and confidence from resumes + profiles

**Bias Detection Agent**  
Evaluates fairness across gender & college metadata

**Matching Agent**  
Evaluates candidates against job requirements and scores them based on technical fit.

**Virtual Interview Panel Agent (AI-Based)**  
Conducts automated, AI-driven virtual interviews to assess technical depth, soft skills, and cultural fit through dynamic questioning.

All agents run as independent services and persist results to the database.

---

## 🧱 Architecture

```
frontend (React)
      |
backend (FastAPI)
      |
PostgreSQL (fairhire)
      |
agent services (Skill, Bias, Matching)
```

- Frontend consumes only REST APIs
- Backend orchestrates workflows and persists all state
- Agents are stateless, backend-controlled microservices

---

## 🚀 Getting Started (Local Development)

### 1. Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Windows / macOS / Linux

---

### 2. Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE fairhire;
```

Ensure credentials are set in `backend/.env`.

---

### 3. Start Agent Services

```bash
cd agents_services
python start_all.py
```

Services:

- **Skill Agent** → `http://127.0.0.1:8001`
- **Bias Agent** → `http://127.0.0.1:8002`
- **Matching Agent** → `http://127.0.0.1:8003`

---

### 4. Start Backend

```bash
cd backend
venv\Scripts\activate   # or source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

Health check:

```
GET http://localhost:8000/health
```

---

### 5. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

---

## 🔄 End-to-End Flow

1. Candidate signs up → receives `anon_id`
2. Company signs up → creates job
3. Candidate applies → skill & bias agents run
4. Company runs matching → candidates selected
5. Virtual Interview Panel conducts automated screening → interview scores generated
6. Dashboards update instantly from DB state

---

## 📊 Dashboards (Live Data)

### Candidate Dashboard

- Active applications
- Selection status
- Skill passport
- Feedback & scores

### Company Dashboard

- Active roles
- Candidates in flow
- Fairness verification status
- Role pipelines

---

## ✅ System Status

- ✔ Fully database-driven
- ✔ No mocked metrics
- ✔ Agents integrated and verified
- ✔ Frontend ↔ backend ↔ agents wired end-to-end
- ✔ Production-style error handling & logging

---

## 📁 Repository Structure

```
.
├── frontend/          # React UI
├── backend/           # FastAPI backend
├── agents_services/   # Agent microservices
└── README.md          # (this file)
```

---

## 🧪 Verification

Example DB checks:

```sql
SELECT id, status, match_score FROM applications ORDER BY id DESC;
SELECT agent_name, status FROM agent_runs ORDER BY id DESC;
```

---

## 📌 Notes

- All auth is local for evaluation clarity
- Designed to be easily extended for production auth later

---
