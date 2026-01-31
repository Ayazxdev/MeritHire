# 🚀 QUICK REFERENCE - COPY THESE FILES

## 📋 File Mapping (What Goes Where)

### Backend Files

```bash
# 1. File Handler Service (NEW)
cp complete_integration/backend/app/services/file_handler.py \
   YOUR_PROJECT/backend/app/services/file_handler.py

# 2. Pipeline Orchestrator (NEW)
cp complete_integration/backend/app/services/pipeline_orchestrator.py \
   YOUR_PROJECT/backend/app/services/pipeline_orchestrator.py

# 3. Updated Candidate Router (REPLACE EXISTING)
cp complete_integration/backend/app/routers/candidate_updated.py \
   YOUR_PROJECT/backend/app/routers/candidate.py
```

### Agent Services

```bash
# Copy all new agent services
cp complete_integration/agents_services/ats_service.py \
   YOUR_PROJECT/agents_services/ats_service.py

cp complete_integration/agents_services/github_service.py \
   YOUR_PROJECT/agents_services/github_service.py

cp complete_integration/agents_services/leetcode_service.py \
   YOUR_PROJECT/agents_services/leetcode_service.py

cp complete_integration/agents_services/linkedin_service.py \
   YOUR_PROJECT/agents_services/linkedin_service.py

cp complete_integration/agents_services/passport_service.py \
   YOUR_PROJECT/agents_services/passport_service.py
```

### Frontend Files

```bash
# 1. Updated Apply Component (REPLACE EXISTING)
cp complete_integration/frontend/src/components/CandidateApply.jsx \
   YOUR_PROJECT/fair-hiring-frontend/src/components/CandidateApply.jsx

# 2. Updated API Client (REPLACE EXISTING)
cp complete_integration/frontend/src/api/backend.js \
   YOUR_PROJECT/fair-hiring-frontend/src/api/backend.js
```

---

## 🔧 Quick Setup (5 Commands)

```bash
# 1. Add PyPDF2 dependency
echo "PyPDF2==3.0.1" >> backend/requirements.txt
pip install PyPDF2==3.0.1

# 2. Update database session maker (if not present)
# Edit backend/app/db.py and ensure async_session_maker is exported

# 3. Copy all files (use commands above)

# 4. Start backend
cd backend && uvicorn app.main:app --reload &

# 5. Start agents
cd agents_services && python start_all_complete.py &
```

---

## ✅ Verify Installation

```bash
# Check all services are running
curl http://localhost:8000/health  # Backend
curl http://localhost:8004/health  # ATS
curl http://localhost:8005/health  # GitHub
curl http://localhost:8006/health  # LeetCode
curl http://localhost:8008/health  # LinkedIn
curl http://localhost:8010/health  # Passport
```

Expected: All return `{"status": "healthy", "service": "..."}`

---

## 🧪 Test Application Flow

1. **Create test PDF**:
```bash
echo "John Doe, Software Engineer, Python, React" > test.txt
# Convert to PDF (or use any existing PDF resume)
```

2. **Open frontend**: http://localhost:5173

3. **Apply to job**:
   - Upload PDF resume
   - Enter GitHub: "octocat"
   - Click "PUSH APPLICATION"

4. **Check status**:
```bash
curl http://localhost:8000/candidate/application/1/status
```

Should show pipeline progress!

---

## 📊 Monitor Pipeline

```bash
# Watch backend logs
tail -f backend/logs/uvicorn.log

# Expected output:
# [PIPELINE] Stage 1: ATS
# [PIPELINE] Stage 2: GitHub
# [PIPELINE] Stage 6: Skill Verification
# [PIPELINE] Pipeline completed
```

---

## 🐛 Common Issues

### "Module not found: file_handler"
**Fix**: Ensure `backend/app/services/` directory exists and contains `__init__.py`
```bash
mkdir -p backend/app/services
touch backend/app/services/__init__.py
```

### "async_session_maker not found"
**Fix**: Update `backend/app/db.py`:
```python
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
```

### "Agent service not responding"
**Fix**: Check if all required ports are free:
```bash
# Check ports
lsof -i :8000-8010

# Kill any conflicting processes
kill -9 <PID>
```

---

## 📚 Full Documentation

For complete details, see:
- **IMPLEMENTATION_SUMMARY.md** - Overview of everything built
- **DEPLOYMENT_GUIDE.md** - Step-by-step deployment
- **INTEGRATION_IMPLEMENTATION.md** - Architecture details

---

## 🎯 Success Indicators

You'll know it's working when:

- ✅ All 10 agent health checks pass
- ✅ Resume PDF uploads successfully
- ✅ Backend logs show "Pipeline completed"
- ✅ Status endpoint returns progress
- ✅ Credential is created with all evidence
- ✅ Match score is calculated

---

## 💡 Pro Tips

1. **Start with health checks** - Verify all services before testing
2. **Check logs first** - Backend logs show exactly what's happening
3. **Use small PDFs** - Test with simple resumes first
4. **Monitor database** - Query credentials table to see state
5. **Test incrementally** - Test each stage individually before full flow

---

## 🚨 Emergency Commands

```bash
# Stop everything
pkill -f uvicorn
pkill -f "python.*service"

# Clear database (CAREFUL!)
psql -d hiring_db -c "TRUNCATE applications, credentials, agent_runs CASCADE;"

# Restart from scratch
cd agents_services && python start_all_complete.py &
cd backend && uvicorn app.main:app --reload &
```

---

## 📞 Need Help?

1. Read **DEPLOYMENT_GUIDE.md** (comprehensive troubleshooting)
2. Check logs in backend and agent services
3. Verify all files are copied correctly
4. Ensure all dependencies are installed

---

**You're ready to go! 🎉**

Copy the files, run the commands, and test the flow.
