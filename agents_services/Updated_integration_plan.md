# 🚀 UPDATED INTEGRATION PLAN
## Based on Your Existing Agent Services

**Status:** You're further along than I thought! ✅  
**What You Have:** 3/10 agent services already built  
**What's Needed:** Complete the remaining 7 agents + orchestrator

---

## ✅ WHAT YOU ALREADY HAVE

### Existing Agent Services (Port 8001-8003)

```
agents_services/
├── skill_agent_service.py      ✅ Port 8001 - Basic skill extraction
├── bias_agent_service.py       ✅ Port 8002 - Bias detection
├── matching_agent_service.py   ✅ Port 8003 - Job matching
├── start_all.py               ✅ Starts all services
└── requirements.txt           ✅ Dependencies
```

**Current Status:**
- All three use **mock/placeholder logic** (TODOs to integrate real agents)
- HTTP endpoints working (`POST /run`, `GET /health`)
- Proper error handling
- Type hints with Pydantic

---

## 🎯 IMMEDIATE ACTION PLAN

### Phase 1: Connect Existing Services to Real Agents (Week 1)

**Goal:** Replace mocks with actual agent implementations

#### Step 1.1: Update `skill_agent_service.py`

**Current State:**
```python
# TODO: Integrate with actual skill verification agent
# Currently using simple heuristics
```

**What to Do:**
```python
# skill_agent_service.py

# Add imports for real agents
from skill_verification_agent.unified_runner import UnifiedSkillRunner
from skill_verification_agent.scraper.unified_scraper import UnifiedScraper

# Initialize at startup
skill_runner = None

@app.on_event("startup")
async def startup():
    global skill_runner
    skill_runner = UnifiedSkillRunner()

@app.post("/run", response_model=SkillAgentResponse)
async def run_skill_verification(request: SkillAgentRequest):
    """Run REAL skill verification"""
    
    try:
        # Use the actual unified runner
        result = await skill_runner.run_complete_workflow(
            resume_text=request.resume_text,
            github_username=extract_username(request.github_url),
            leetcode_username=extract_username(request.leetcode_url),
            codeforces_handle=extract_username(request.codeforces_url),
            linkedin_pdf_path=request.linkedin_url  # Or handle URL
        )
        
        # Map to expected output format
        return SkillAgentResponse(
            output={
                "skills": result.get("verified_skills", []),
                "confidence": result.get("skill_confidence", 0),
                "signal_strength": result.get("signal_strength", "weak"),
                "test_required": result.get("credential_status") == "PENDING_TEST"
            },
            explanation=result.get("explanation", ""),
            flags=result.get("flags", [])
        )
    
    except Exception as e:
        logger.error(f"Skill verification failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

**Helper function:**
```python
def extract_username(url: str) -> str:
    """Extract username from profile URL"""
    if not url:
        return None
    # GitHub: https://github.com/Udbhaw08 → Udbhaw08
    # LeetCode: https://leetcode.com/username → username
    # Codeforces: https://codeforces.com/profile/handle → handle
    parts = url.rstrip('/').split('/')
    return parts[-1] if parts else None
```

---

#### Step 1.2: Update `bias_agent_service.py`

**Current State:**
```python
# TODO: Integrate with actual bias detection agent
# Mock logic: flag if confidence > 95
```

**What to Do:**
```python
# bias_agent_service.py

from bias_detection_agent.agents.bias_detection_agent import BiasDetectionAgent

bias_agent = None

@app.on_event("startup")
async def startup():
    global bias_agent
    bias_agent = BiasDetectionAgent()

@app.post("/run", response_model=BiasAgentResponse)
async def run_bias_detection(request: BiasAgentRequest):
    """Run REAL bias detection"""
    
    try:
        # Call actual bias agent
        result = await bias_agent.analyze_batch(
            credentials=[request.credential],
            metadata=[request.metadata],
            mode=request.mode
        )
        
        # Extract first result (batch of 1)
        analysis = result[0] if result else {}
        
        return BiasAgentResponse(
            bias_detected=analysis.get("bias_detected", False),
            action=analysis.get("action", "proceed_to_matching"),
            severity=analysis.get("severity", "none"),
            checks={
                "gender_bias": analysis.get("gender_bias", {}),
                "college_bias": analysis.get("college_bias", {}),
                "systemic_issues": analysis.get("systemic_issues", [])
            }
        )
    
    except Exception as e:
        logger.error(f"Bias detection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

#### Step 1.3: Update `matching_agent_service.py`

**Current State:**
```python
# TODO: Integrate with actual matching agent
# Simple keyword matching
```

**What to Do:**
```python
# matching_agent_service.py

from matching_agent.agents.matching_agent import MatchingAgent

matching_agent = None

@app.on_event("startup")
async def startup():
    global matching_agent
    matching_agent = MatchingAgent()

@app.post("/run", response_model=MatchAgentResponse)
async def run_matching(request: MatchAgentRequest):
    """Run REAL matching agent"""
    
    try:
        # Call actual matching agent
        result = await matching_agent.match(
            credential=request.credential,
            job_description=request.job_description.get("description", ""),
            job_requirements={
                "required_skills": request.job_description.get("required_skills", []),
                "preferred_skills": request.job_description.get("preferred_skills", [])
            }
        )
        
        return MatchAgentResponse(
            match_score=result.get("overall_score", 0),
            matched_skills=result.get("matched_skills", []),
            missing_skills=result.get("missing_skills", []),
            recommendation=result.get("recommendation", ""),
            breakdown={
                "core_skills": result.get("core_match", 0),
                "frameworks": result.get("framework_match", 0),
                "experience": result.get("experience_match", 0)
            }
        )
    
    except Exception as e:
        logger.error(f"Matching failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Phase 2: Create Missing Agent Services (Week 2)

You need **7 more agent services** to complete the pipeline:

#### New Services to Create:

```
agents_services/
├── ats_service.py              🆕 Port 8004 - Fraud detection
├── github_service.py           🆕 Port 8005 - GitHub scraping
├── leetcode_service.py         🆕 Port 8006 - LeetCode scraping
├── codeforces_service.py       🆕 Port 8007 - Codeforces scraping
├── linkedin_service.py         🆕 Port 8008 - LinkedIn parsing
├── conditional_test_service.py 🆕 Port 8009 - Test generation
└── passport_service.py         🆕 Port 8010 - Credential signing
```

**Why separate them?**
1. Better error isolation (one scraper fails ≠ whole pipeline fails)
2. Can scale independently
3. Easier to test
4. Matches your 10-stage pipeline

---

#### Template for New Services:

```python
# agents_services/ats_service.py
"""
ATS Fraud Detection Service
Port: 8004
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents_files', 'Clean_Hiring_System'))

from skill_verification_agent.agents.ats import ATSAgent

app = FastAPI(title="ATS Service", version="1.0.0")
ats_agent = None

@app.on_event("startup")
async def startup():
    global ats_agent
    ats_agent = ATSAgent()

class ATSRequest(BaseModel):
    resume_text: str

class ATSResponse(BaseModel):
    status: str  # OK | NEEDS_REVIEW | BLACKLISTED
    fraud_detected: bool
    needs_review: bool
    reason: str
    manipulation_signals: dict

@app.post("/analyze", response_model=ATSResponse)
async def analyze_resume(request: ATSRequest):
    try:
        result = await ats_agent.analyze(request.resume_text)
        
        return ATSResponse(
            status=result.get("final_action", "OK"),
            fraud_detected=result.get("final_action") == "BLACKLISTED",
            needs_review=result.get("final_action") == "PENDING_HUMAN_REVIEW",
            reason=result.get("human_review_reason", ""),
            manipulation_signals=result.get("manipulation_signals", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ats"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
```

---

### Phase 3: Update Backend to Use Services (Week 3)

#### Current Backend Code (candidate.py):

```python
# This is SYNCHRONOUS and only uses 2 agents
result = await call_skill_agent(agent_input)
bias_result = await call_bias_agent(bias_input)
```

#### What to Change:

**Option A: Quick Fix (Keep Synchronous for V1)**

Update `backend/app/routers/candidate.py`:

```python
@router.post("/apply")
async def apply(payload: ApplyRequest, db: AsyncSession = Depends(get_db)):
    # ... existing candidate/blacklist checks ...
    
    # Create application
    app = Application(...)
    db.add(app)
    await db.commit()
    
    # Initialize state
    state = {
        "application_id": app.id,
        "pipeline_status": "in_progress",
        "stages_completed": [],
        "evidence": {}
    }
    
    # STAGE 1: ATS
    try:
        ats_result = await call_service("http://localhost:8004/analyze", {
            "resume_text": payload.resume_text
        })
        
        if ats_result["fraud_detected"]:
            # Blacklist immediately
            blacklist_entry = Blacklist(
                candidate_id=cand.id,
                reason=ats_result["reason"]
            )
            db.add(blacklist_entry)
            app.status = "rejected"
            await db.commit()
            return {"application_id": app.id, "status": "rejected", "reason": "fraud_detected"}
        
        if ats_result["needs_review"]:
            # Create review case
            review_case = ReviewCase(
                application_id=app.id,
                job_id=app.job_id,
                candidate_id=cand.id,
                triggered_by="ATS",
                severity="high",
                reason=ats_result["reason"],
                evidence=ats_result["manipulation_signals"]
            )
            db.add(review_case)
            app.status = "needs_review"
            await db.commit()
            return {"application_id": app.id, "status": "needs_review"}
        
        state["evidence"]["ats"] = ats_result
        state["stages_completed"].append("ATS")
        
    except Exception as e:
        logger.error(f"ATS failed: {str(e)}")
        app.status = "error"
        await db.commit()
        return {"application_id": app.id, "status": "error"}
    
    # STAGE 2-5: Scrapers (GitHub, LeetCode, etc.)
    scraper_results = {}
    
    if payload.github_url:
        scraper_results["github"] = await call_service("http://localhost:8005/scrape", {
            "url": payload.github_url
        })
    
    if payload.leetcode_url:
        scraper_results["leetcode"] = await call_service("http://localhost:8006/scrape", {
            "url": payload.leetcode_url
        })
    
    # ... similar for codeforces, linkedin ...
    
    state["evidence"].update(scraper_results)
    state["stages_completed"].extend(["GITHUB", "LEETCODE", "CODEFORCES", "LINKEDIN"])
    
    # STAGE 6: Skill Verification (Aggregation)
    skill_result = await call_service("http://localhost:8001/run", {
        "application_id": app.id,
        "resume_text": payload.resume_text,
        "github_url": payload.github_url,
        "leetcode_url": payload.leetcode_url,
        "codeforces_url": payload.codeforces_url,
        "linkedin_url": payload.linkedin_url,
        "anon_id": payload.anon_id
    })
    
    state["evidence"]["skills"] = skill_result
    state["verified_skills"] = skill_result["output"]["skills"]
    state["confidence"] = skill_result["output"]["confidence"]
    
    # STAGE 7: Conditional Test (if required)
    if skill_result["output"].get("test_required"):
        app.test_required = True
        app.status = "pending_test"
        await db.commit()
        
        # Save state for resume later
        await save_state(db, app.id, state)
        
        return {
            "application_id": app.id,
            "status": "pending_test",
            "message": "Please complete the skill test"
        }
    
    state["stages_completed"].append("SKILL_VERIFICATION")
    
    # STAGE 8: Bias Detection
    bias_result = await call_service("http://localhost:8002/run", {
        "credential": state["evidence"],
        "metadata": {
            "gender": cand.gender or "unknown",
            "college": cand.college or "unknown"
        },
        "mode": "realtime"
    })
    
    state["evidence"]["bias"] = bias_result
    
    if bias_result["severity"] in ["high", "critical"]:
        review_case = ReviewCase(
            application_id=app.id,
            job_id=app.job_id,
            candidate_id=cand.id,
            triggered_by="BIAS_DETECTION",
            severity=bias_result["severity"],
            reason="Bias detection flagged systemic issues",
            evidence=bias_result
        )
        db.add(review_case)
        # Note: Don't stop pipeline for bias (continue to matching)
    
    state["stages_completed"].append("BIAS_DETECTION")
    
    # STAGE 9: Matching
    job = await db.execute(select(Job).where(Job.id == app.job_id))
    job = job.scalar_one()
    
    match_result = await call_service("http://localhost:8003/run", {
        "credential": state["evidence"],
        "job_description": {
            "title": job.title,
            "description": job.description,
            "required_skills": []  # TODO: extract from job
        }
    })
    
    state["evidence"]["matching"] = match_result
    state["match_score"] = match_result["match_score"]
    app.match_score = match_result["match_score"]
    
    state["stages_completed"].append("MATCHING")
    
    # STAGE 10: Passport
    passport_result = await call_service("http://localhost:8010/issue", {
        "application_id": app.id,
        "credential_data": state["evidence"],
        "match_score": match_result["match_score"]
    })
    
    # Save credential
    from app.passport import sign_credential
    h, sig = sign_credential(state["evidence"])
    
    cred = Credential(
        candidate_id=cand.id,
        application_id=app.id,
        credential_json=state["evidence"],
        hash_sha256=h,
        signature_b64=sig
    )
    db.add(cred)
    
    state["credential_id"] = passport_result["credential_id"]
    state["stages_completed"].append("PASSPORT")
    state["pipeline_status"] = "completed"
    
    # Finalize
    app.status = "matched" if match_result["match_score"] >= 60 else "rejected"
    app.feedback_json = {
        "matched_skills": match_result.get("matched_skills", []),
        "missing_skills": match_result.get("missing_skills", [])
    }
    
    await db.commit()
    
    return {
        "application_id": app.id,
        "status": app.status,
        "match_score": app.match_score,
        "credential_id": cred.id
    }


# Helper function
async def call_service(url: str, payload: dict) -> dict:
    """Call an agent service and return result"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()
```

**Helper to save/load state:**

```python
# backend/app/services/state_manager.py (simple version)

async def save_state(db: AsyncSession, application_id: int, state: dict):
    """Save pipeline state to credential_json"""
    from app.models import Application, Credential
    
    app = await db.execute(select(Application).where(Application.id == application_id))
    app = app.scalar_one()
    
    # Check if credential exists
    cred_q = await db.execute(
        select(Credential)
        .where(Credential.application_id == application_id)
        .order_by(Credential.issued_at.desc())
    )
    cred = cred_q.scalar_one_or_none()
    
    if cred:
        cred.credential_json = state
    else:
        from app.passport import sign_credential
        h, sig = sign_credential(state)
        
        cred = Credential(
            candidate_id=app.candidate_id,
            application_id=application_id,
            credential_json=state,
            hash_sha256=h,
            signature_b64=sig
        )
        db.add(cred)
    
    await db.commit()


async def load_state(db: AsyncSession, application_id: int) -> dict:
    """Load pipeline state from credential_json"""
    from app.models import Credential
    
    cred_q = await db.execute(
        select(Credential)
        .where(Credential.application_id == application_id)
        .order_by(Credential.issued_at.desc())
    )
    cred = cred_q.scalar_one_or_none()
    
    return cred.credential_json if cred else None
```

---

**Option B: Full Orchestrator (Async with Celery) - Do This in Week 4-5**

Keep the original orchestrator plan but it runs in background worker.

---

## 📋 REVISED CHECKLIST

### Week 1: Connect Real Agents ✅
- [ ] Update `skill_agent_service.py` to use UnifiedSkillRunner
- [ ] Update `bias_agent_service.py` to use BiasDetectionAgent
- [ ] Update `matching_agent_service.py` to use MatchingAgent
- [ ] Test each service individually with curl/Postman
- [ ] Update `start_all.py` if needed

### Week 2: Create Missing Services 🆕
- [ ] Create `ats_service.py` (Port 8004)
- [ ] Create `github_service.py` (Port 8005)
- [ ] Create `leetcode_service.py` (Port 8006)
- [ ] Create `codeforces_service.py` (Port 8007)
- [ ] Create `linkedin_service.py` (Port 8008)
- [ ] Create `conditional_test_service.py` (Port 8009)
- [ ] Create `passport_service.py` (Port 8010)
- [ ] Update `start_all.py` to launch all 10 services
- [ ] Test complete service mesh

### Week 3: Backend Integration ⚡
- [ ] Create `state_manager.py` (save/load state)
- [ ] Update `candidate.py` to call all 10 services in sequence
- [ ] Add error handling for each stage
- [ ] Add human-in-loop for ATS/Bias
- [ ] Add test submission endpoint
- [ ] Test end-to-end flow

### Week 4: Admin & Polish 🎨
- [ ] Create admin review endpoints
- [ ] Add status polling endpoint
- [ ] Frontend integration
- [ ] Load testing
- [ ] Deploy to staging

---

## 🚀 QUICKSTART (What to Do RIGHT NOW)

**Step 1: Test Your Current Services**

```bash
# Start existing services
cd agents_services
python start_all.py
```

**Step 2: Test with curl**

```bash
# Test skill agent
curl -X POST http://localhost:8001/run \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": 1,
    "resume_text": "Python developer with FastAPI experience",
    "github_url": "https://github.com/Udbhaw08",
    "anon_id": "test123"
  }'

# Test bias agent
curl -X POST http://localhost:8002/run \
  -H "Content-Type: application/json" \
  -d '{
    "credential": {"confidence": 85, "skills": ["Python"]},
    "metadata": {"gender": "unknown", "college": "IIT"},
    "mode": "realtime"
  }'

# Test matching agent
curl -X POST http://localhost:8003/run \
  -H "Content-Type: application/json" \
  -d '{
    "credential": {"confidence": 85, "skills": ["Python", "FastAPI"]},
    "job_description": {
      "title": "Backend Engineer",
      "description": "Looking for Python FastAPI developer"
    }
  }'
```

**Step 3: Pick Your Path**

- **Want quick results?** → Update the 3 existing services to use real agents
- **Want complete system?** → Create all 7 missing services first
- **Want production-ready?** → Follow the full orchestrator plan

**What sounds best for your timeline?** Tell me and I'll give you the exact code to implement!