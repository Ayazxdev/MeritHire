# COMPLETE DEPLOYMENT & TESTING GUIDE

## 🚀 Quick Start

This guide provides step-by-step instructions to deploy and test the complete end-to-end integration.

## 📁 File Structure

```
project/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   └── candidate.py  ← REPLACE with candidate_updated.py
│   │   ├── services/
│   │   │   ├── file_handler.py  ← NEW
│   │   │   └── pipeline_orchestrator.py  ← NEW
│   │   ├── models.py
│   │   └── main.py
│   └── requirements.txt  ← ADD PyPDF2
├── agents_services/
│   ├── ats_service.py  ← NEW
│   ├── github_service.py  ← NEW
│   ├── leetcode_service.py  ← NEW
│   ├── linkedin_service.py  ← NEW
│   ├── passport_service.py  ← NEW
│   ├── skill_agent_service.py  ← EXISTING
│   ├── bias_agent_service.py  ← EXISTING
│   ├── matching_agent_service.py  ← EXISTING
│   ├── codeforce_service.py  ← EXISTING
│   ├── conditional_test_service.py  ← EXISTING
│   └── start_all_complete.py  ← EXISTING
└── frontend/
    └── src/
        ├── components/
        │   └── CandidateApply.jsx  ← REPLACE
        └── api/
            └── backend.js  ← REPLACE
```

## 🔧 Installation Steps

### 1. Backend Setup

```bash
cd backend

# Add PyPDF2 to requirements.txt
echo "PyPDF2==3.0.1" >> requirements.txt

# Install dependencies
pip install -r requirements.txt

# Copy new files
cp /path/to/candidate_updated.py app/routers/candidate.py
mkdir -p app/services
cp /path/to/file_handler.py app/services/
cp /path/to/pipeline_orchestrator.py app/services/

# Update imports in app/main.py if needed
# Ensure async_session_maker is exported from db.py
```

**Update `app/db.py`** to export session maker:

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# ... existing code ...

async_session_maker = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db():
    async with async_session_maker() as session:
        yield session
```

**Update `backend/requirements.txt`**:

```txt
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
pydantic==2.5.0
python-multipart==0.0.6
bcrypt==4.1.1
httpx==0.25.2
PyPDF2==3.0.1
```

### 2. Agent Services Setup

```bash
cd agents_services

# Copy new services
cp /path/to/ats_service.py .
cp /path/to/github_service.py .
cp /path/to/leetcode_service.py .
cp /path/to/linkedin_service.py .
cp /path/to/passport_service.py .

# Verify all services exist
ls -la *.py
```

**Expected services:**
- ats_service.py (Port 8004)
- github_service.py (Port 8005)
- leetcode_service.py (Port 8006)
- codeforce_service.py (Port 8007)
- linkedin_service.py (Port 8008)
- skill_agent_service.py (Port 8001)
- conditional_test_service.py (Port 8009)
- bias_agent_service.py (Port 8002)
- matching_agent_service.py (Port 8003)
- passport_service.py (Port 8010)

### 3. Frontend Setup

```bash
cd fair-hiring-frontend

# Copy updated files
cp /path/to/CandidateApply.jsx src/components/
cp /path/to/backend.js src/api/

# Install dependencies (if not already done)
npm install

# Build
npm run build
```

## 🚦 Starting the System

### Terminal 1: Database (if not running)

```bash
# PostgreSQL should be running
# Check with: pg_isready
```

### Terminal 2: Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Terminal 3: Agent Services

```bash
cd agents_services
python start_all_complete.py
```

Wait for all services to show "✅ All services are up"

### Terminal 4: Frontend

```bash
cd fair-hiring-frontend
npm run dev
```

## 🧪 Testing the Integration

### Test 1: Health Checks

```bash
# Check all agent services
curl http://localhost:8004/health  # ATS
curl http://localhost:8005/health  # GitHub
curl http://localhost:8006/health  # LeetCode
curl http://localhost:8007/health  # Codeforces
curl http://localhost:8008/health  # LinkedIn
curl http://localhost:8001/health  # Skill
curl http://localhost:8009/health  # Test
curl http://localhost:8002/health  # Bias
curl http://localhost:8003/health  # Matching
curl http://localhost:8010/health  # Passport

# Check backend
curl http://localhost:8000/health
```

### Test 2: End-to-End Application Flow

**Step 1: Create a test PDF resume**

```bash
# Create a simple test resume
echo "John Doe
Software Engineer
Experience: Python, JavaScript, React
GitHub: johndoe
Projects: Built multiple web apps" > test_resume.txt

# Convert to PDF (on Linux/Mac)
# Install pandoc if needed: apt-get install pandoc texlive-latex-base
pandoc test_resume.txt -o test_resume.pdf
```

**Step 2: Sign up as candidate**

1. Open http://localhost:5173
2. Click "Candidate Login"
3. Sign up with email/password
4. Note the `anon_id` stored in localStorage

**Step 3: Apply to a job**

1. Navigate to job listings
2. Click "Apply" on a job
3. Upload test_resume.pdf
4. Enter GitHub username (e.g., "octocat")
5. Optionally add LeetCode, Codeforces, LinkedIn
6. Click "PUSH APPLICATION"

**Step 4: Monitor pipeline**

Watch the backend logs to see pipeline execution:

```
[PIPELINE] Stage 1: ATS - application_id=1
[PIPELINE] ATS completed successfully
[PIPELINE] Stage 2: GitHub - application_id=1
[PIPELINE] GitHub completed successfully
[PIPELINE] Stage 3: LeetCode - application_id=1
... (continues through all 10 stages)
[PIPELINE] Pipeline completed for application 1
```

**Step 5: Check application status**

```bash
# Poll status endpoint
curl http://localhost:8000/candidate/application/1/status
```

Expected response:

```json
{
  "application_id": 1,
  "status": "completed",
  "current_stage": "COMPLETE",
  "stages_completed": ["ATS", "GITHUB", "SKILL", "BIAS", "MATCHING", "PASSPORT"],
  "total_stages": 10,
  "progress_percentage": 100,
  "credential_preview": {
    "confidence": 70,
    "skills": ["Python", "JavaScript", "React"],
    "github_verified": true,
    "leetcode_verified": false
  },
  "match_score": 75
}
```

### Test 3: Test Required Flow

To test the conditional test flow:

1. Modify `skill_agent_service.py` to always return `test_required: true`
2. Apply to a job
3. Pipeline will pause at SKILL stage
4. Frontend should show test interface
5. Submit test with score
6. Pipeline should resume

### Test 4: Review Case Flow

To test human review:

1. Create a resume with suspicious content (e.g., "ignore all previous instructions")
2. Apply to job
3. ATS should detect and create ReviewCase
4. Application status should be "needs_review"
5. Admin dashboard should show the case

## 🐛 Troubleshooting

### Issue: "Resume processing failed"

**Cause**: PyPDF2 not installed or PDF is encrypted/scanned

**Solution**:
```bash
pip install PyPDF2==3.0.1
# Use text-based PDF, not scanned image
```

### Issue: "Agent service not responding"

**Cause**: Service not started or port conflict

**Solution**:
```bash
# Check if port is in use
lsof -i :8004  # Replace with specific port

# Kill process if needed
kill -9 <PID>

# Restart services
python start_all_complete.py
```

### Issue: "Invalid anon_id"

**Cause**: LocalStorage cleared or candidate not logged in

**Solution**:
- Log in again as candidate
- Check browser console for `fhn_candidate_anon_id`

### Issue: "Pipeline not progressing"

**Cause**: One agent service failed

**Solution**:
- Check backend logs for specific agent failure
- Check agent service logs
- Verify all services are healthy

### Issue: "CORS error in frontend"

**Cause**: Backend not allowing frontend origin

**Solution**:
```python
# In backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 Monitoring

### View Pipeline State

```bash
# Query credential state directly
psql -d hiring_db -c "
  SELECT 
    application_id,
    credential_json->>'status' as status,
    credential_json->>'current_stage' as stage,
    credential_json->'stages_completed' as completed
  FROM credentials 
  ORDER BY issued_at DESC 
  LIMIT 5;
"
```

### View Agent Runs

```bash
psql -d hiring_db -c "
  SELECT 
    application_id,
    agent_name,
    status,
    created_at
  FROM agent_runs
  WHERE application_id = 1
  ORDER BY created_at;
"
```

### View Application Status

```bash
psql -d hiring_db -c "
  SELECT 
    id,
    status,
    test_required,
    match_score,
    created_at
  FROM applications
  WHERE id = 1;
"
```

## 🔍 API Reference

### POST /candidate/apply

**FormData Fields:**
- `job_id` (int, required)
- `anon_id` (string, required)
- `resume` (file, required) - PDF only
- `github` (string, required)
- `leetcode` (string, optional)
- `codeforces` (string, optional)
- `linkedin_pdf` (file, optional) - PDF only

**Response:**
```json
{
  "application_id": 1,
  "status": "processing",
  "message": "Application submitted. Pipeline is running."
}
```

### GET /candidate/application/{id}/status

**Response:**
```json
{
  "application_id": 1,
  "status": "processing | test_required | needs_review | completed | rejected",
  "current_stage": "GITHUB | SKILL | MATCHING | etc.",
  "stages_completed": ["ATS", "GITHUB", "SKILL"],
  "total_stages": 10,
  "progress_percentage": 30,
  "credential_preview": {
    "confidence": 65,
    "skills": ["Python", "React"],
    "github_verified": true
  },
  "test_required": false,
  "match_score": null,
  "error": null
}
```

### POST /candidate/application/{id}/submit-test

**FormData Fields:**
- `test_score` (int, required) - Score 0-100
- `test_data` (string, optional) - JSON string of full test results

**Response:**
```json
{
  "application_id": 1,
  "status": "processing",
  "message": "Test submitted. Pipeline resumed."
}
```

## 🎯 Success Criteria

The system is working correctly when:

1. ✅ All 10 agent services respond to health checks
2. ✅ Backend accepts file uploads (resume PDF)
3. ✅ Pipeline executes all stages sequentially
4. ✅ Application status updates in real-time
5. ✅ Test required flow pauses and resumes pipeline
6. ✅ Bias/ATS review cases are created when triggered
7. ✅ Final credential is issued with all evidence
8. ✅ Match score is calculated and stored

## 📝 Next Steps

After confirming basic functionality:

1. **Replace mock agents** with real implementations from `agents_files/Clean_Hiring_System`
2. **Add frontend polling** for real-time UI updates
3. **Implement ApplicationStatus component** to show pipeline progress
4. **Add test interface** for conditional test flow
5. **Enhance error handling** for agent failures
6. **Add retry logic** for failed agent calls
7. **Implement notification system** for status changes

## 🔐 Security Checklist

Before production:

- [ ] Enable authentication on all endpoints
- [ ] Validate file uploads (size, type, content)
- [ ] Sanitize all user inputs
- [ ] Use HTTPS for all communications
- [ ] Encrypt sensitive data at rest
- [ ] Implement rate limiting
- [ ] Add CSRF protection
- [ ] Audit log all actions
- [ ] Use environment variables for secrets
- [ ] Enable CORS only for trusted origins

## 📚 Additional Resources

- Backend API Docs: http://localhost:8000/docs
- Agent Services: Ports 8001-8010
- Database Schema: See `backend/app/models.py`
- Pipeline Flow: See `INTEGRATION_IMPLEMENTATION.md`

---

## 🎉 You're All Set!

The complete end-to-end integration is now deployed and testable. Monitor the logs, test the flow, and iterate based on feedback.

For questions or issues, check the troubleshooting section above.
