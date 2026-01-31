# COMPLETE END-TO-END INTEGRATION IMPLEMENTATION

## Overview
This document provides the complete implementation for integrating the candidate application flow with the full agent pipeline, including:
- File upload handling (PDFs)
- Complete 10-stage pipeline orchestration
- Real-time status updates
- All missing agent services
- Frontend-backend integration

## Architecture

```
FRONTEND (React)
    ↓ FormData (multipart/form-data)
BACKEND API (/candidate/apply)
    ↓ Store files, extract text, create Application
PIPELINE ORCHESTRATOR
    ↓ Sequential agent execution
    ├─→ Stage 1: ATS (Fraud Detection)
    ├─→ Stage 2: GitHub Scraper
    ├─→ Stage 3: LeetCode Scraper
    ├─→ Stage 4: Codeforces Scraper
    ├─→ Stage 5: LinkedIn Parser
    ├─→ Stage 6: Skill Verification
    ├─→ Stage 7: Conditional Test (if required)
    ├─→ Stage 8: Bias Detection
    ├─→ Stage 9: Matching
    └─→ Stage 10: Passport Issuance
    ↓
CREDENTIAL + STATUS UPDATES
    ↓
FRONTEND POLLING (/candidate/application/{id}/status)
```

## Implementation Steps

### Phase 1: Backend File Handling & Pipeline
### Phase 2: Complete Agent Services
### Phase 3: Frontend Integration
### Phase 4: Real-time Status Updates

---

## FILES TO CREATE/MODIFY

### Backend
1. `backend/app/routers/candidate.py` - UPDATE
2. `backend/app/services/pipeline_orchestrator.py` - NEW
3. `backend/app/services/file_handler.py` - NEW
4. `backend/app/models.py` - UPDATE (add evaluation_id, pipeline state)

### Agent Services
5. `agents_services/ats_service.py` - NEW
6. `agents_services/github_service.py` - NEW
7. `agents_services/leetcode_service.py` - NEW
8. `agents_services/codeforce_service.py` - UPDATE
9. `agents_services/linkedin_service.py` - NEW
10. `agents_services/conditional_test_service.py` - NEW
11. `agents_services/passport_service.py` - NEW

### Frontend
12. `frontend/src/components/CandidateApply.jsx` - UPDATE
13. `frontend/src/api/backend.js` - UPDATE
14. `frontend/src/components/ApplicationStatus.jsx` - NEW

---

## KEY IMPLEMENTATION DETAILS

### 1. File Upload Flow
- Frontend sends `multipart/form-data` with:
  - `resume` (File, required)
  - `github` (string)
  - `leetcode` (string, optional)
  - `codeforces` (string, optional)
  - `linkedin_pdf` (File, optional)
  - `job_id` (int)

- Backend:
  - Stores files in `/uploads/{anon_id}/{application_id}/`
  - Extracts text from PDFs using PyPDF2
  - Creates Application record with file paths
  - Enqueues pipeline execution

### 2. Pipeline State Machine
States: `INIT → ATS → GITHUB → LEETCODE → CODEFORCES → LINKEDIN → SKILL → TEST? → BIAS → MATCHING → PASSPORT → COMPLETE`

Each stage:
- Updates `credential_state` JSON
- Stores evidence
- Can trigger PAUSE (for test or review)
- Emits status to DB

### 3. Credential Evolution
```json
{
  "application_id": "...",
  "status": "processing | needs_review | test_required | completed",
  "current_stage": "SKILL | TEST | MATCH",
  "stages_completed": ["ATS", "GITHUB", ...],
  "evidence": {
    "ats": {...},
    "github": {...},
    "leetcode": {...},
    "skills": [...],
    "test_score": 85,
    "bias_report": {...},
    "match_score": 70
  },
  "flags": [],
  "test_required": false,
  "credential_status": "VERIFIED | PROVISIONAL | REJECTED"
}
```

### 4. Real-time Updates
Frontend polls: `GET /candidate/application/{id}/status`

Response:
```json
{
  "application_id": 123,
  "status": "processing",
  "current_stage": "GITHUB",
  "stages_completed": ["ATS"],
  "total_stages": 10,
  "progress_percentage": 10,
  "credential_preview": {
    "confidence": 0,
    "skills": []
  },
  "test_required": false,
  "error": null
}
```

Poll every 2 seconds while `status === "processing"`

---

## ERROR HANDLING

### ATS Rejection
- Action: BLACKLIST candidate
- Status: `rejected`
- Pipeline: TERMINATE

### Bias High/Critical
- Action: Create ReviewCase
- Status: `needs_review`
- Pipeline: PAUSE → wait for admin

### Test Required
- Action: None (frontend shows test)
- Status: `test_required`
- Pipeline: PAUSE → resume after test submission

### Agent Failure
- Action: Retry 3x, then mark stage as failed
- Status: `processing` (continues)
- Pipeline: CONTINUE with partial evidence

---

## IMPLEMENTATION CHECKLIST

- [ ] Update backend models (add Evaluation, PipelineState)
- [ ] Create file_handler.py for PDF processing
- [ ] Create pipeline_orchestrator.py
- [ ] Update candidate.py router with file upload
- [ ] Create status endpoint
- [ ] Create all 7 missing agent services
- [ ] Update CandidateApply.jsx with FormData
- [ ] Create ApplicationStatus.jsx component
- [ ] Add polling logic
- [ ] Add error handling
- [ ] Test end-to-end flow
