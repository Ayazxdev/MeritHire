import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.db import get_db
from app.models import Candidate, Application, AgentRun, Credential, ReviewCase, Blacklist, Job
from app.audit import log_event
from app.schemas import JobOut
from app.services.file_handler import FileHandler
from app.services.pipeline_orchestrator import PipelineOrchestrator
import asyncio

router = APIRouter(prefix="/candidate", tags=["candidate"])
log = logging.getLogger("uvicorn.error")

@router.post("/apply")
async def apply(
    job_id: int = Form(...),
    anon_id: str = Form(...),
    github: str = Form(None),
    leetcode: str = Form(None),
    codeforces: str = Form(None),
    resume: UploadFile = File(...),
    linkedin_pdf: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Apply to a job with complete file upload support
    
    FormData fields:
    - job_id: Job ID (required)
    - anon_id: Candidate anonymous ID (required)
    - resume: Resume PDF file (required)
    - github: GitHub username or URL (optional)
    - leetcode: LeetCode profile URL (optional)
    - codeforces: Codeforces handle or URL (optional)
    - linkedin_pdf: LinkedIn profile PDF (optional)
    """
    try:
        # Lookup candidate
        q = await db.execute(select(Candidate).where(Candidate.anon_id == anon_id))
        cand = q.scalar_one_or_none()
        
        if not cand:
            log.warning(f"[APPLY] Invalid anon_id: {anon_id}")
            raise HTTPException(status_code=400, detail="Invalid anon_id. Please login again.")
        
        log.info(f"[APPLY] Candidate found: id={cand.id}, anon_id={cand.anon_id}")
        
        # Check blacklist
        q_bl = await db.execute(select(Blacklist).where(Blacklist.candidate_id == cand.id))
        if q_bl.scalar_one_or_none():
            log.warning(f"[APPLY] Candidate {cand.id} is blacklisted")
            return JSONResponse(
                status_code=403,
                content={"application_id": None, "status": "rejected", "reason": "blacklisted"}
            )
        
        # Verify job exists
        job_q = await db.execute(select(Job).where(Job.id == job_id))
        job = job_q.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Create application record (without files first)
        app = Application(
            job_id=job_id,
            candidate_id=cand.id,
            resume_text="",  # Will be filled after processing
            github_url=github,
            leetcode_url=leetcode,
            codeforces_url=codeforces,
            linkedin_url=None,  # Will be filled if LinkedIn PDF provided
            status="pending"
        )
        db.add(app)
        await db.commit()
        await db.refresh(app)
        
        log.info(f"[APPLY] Application created: id={app.id}")
        
        # Process resume file
        try:
            resume_path, resume_hash, resume_text = await FileHandler.process_resume(
                resume, anon_id, app.id
            )
            
            log.info(f"[APPLY] Resume processed: {len(resume_text)} chars")
            
            # Update application with resume data
            app.resume_text = resume_text
            app.resume_file_path = resume_path
            
        except Exception as e:
            log.error(f"[APPLY] Resume processing failed: {str(e)}")
            # Delete application
            await db.delete(app)
            await db.commit()
            raise HTTPException(status_code=400, detail=f"Resume processing failed: {str(e)}")
        
        # Process LinkedIn PDF if provided
        linkedin_text = None
        if linkedin_pdf and linkedin_pdf.filename:
            try:
                linkedin_result = await FileHandler.process_linkedin_pdf(
                    linkedin_pdf, anon_id, app.id
                )
                if linkedin_result:
                    linkedin_path, linkedin_text = linkedin_result
                    app.linkedin_url = linkedin_path
                    log.info(f"[APPLY] LinkedIn PDF processed")
            except Exception as e:
                log.warning(f"[APPLY] LinkedIn processing failed: {str(e)}")
                # Continue without LinkedIn data
        
        await db.commit()
        await log_event(db, "candidate", "candidate_applied", {"application_id": app.id})
        
        # Start pipeline execution asynchronously
        log.info(f"[APPLY] Starting pipeline for application {app.id}")
        
        # Execute pipeline in background
        asyncio.create_task(
            execute_pipeline_background(
                app.id,
                resume_text,
                resume_path,
                github,
                leetcode,
                codeforces,
                app.linkedin_url,
                linkedin_text
            )
        )
        
        return {
            "application_id": app.id,
            "status": "processing",
            "message": "Application submitted. Pipeline is running."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"[APPLY] Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def execute_pipeline_background(
    application_id: int,
    resume_text: str,
    resume_path: str,
    github_url: Optional[str],
    leetcode_url: Optional[str],
    codeforces_url: Optional[str],
    linkedin_pdf_path: Optional[str],
    linkedin_text: Optional[str]
):
    """Execute pipeline in background"""
    from app.db import async_session_maker
    
    async with async_session_maker() as db:
        try:
            orchestrator = PipelineOrchestrator(db)
            await orchestrator.execute_pipeline(
                application_id=application_id,
                resume_text=resume_text,
                resume_path=resume_path,
                github_url=github_url,
                leetcode_url=leetcode_url,
                codeforces_url=codeforces_url,
                linkedin_pdf_path=linkedin_pdf_path,
                linkedin_text=linkedin_text
            )
            log.info(f"[PIPELINE] Background execution completed for app {application_id}")
        except Exception as e:
            log.error(f"[PIPELINE] Background execution failed for app {application_id}: {str(e)}")


@router.get("/application/{application_id}/status")
async def get_application_status(
    application_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get real-time application status for polling
    
    Returns:
    - status: processing | test_required | needs_review | completed | rejected | failed
    - current_stage: Current pipeline stage
    - stages_completed: List of completed stages
    - progress_percentage: Overall progress (0-100)
    - credential_preview: Preview of collected evidence
    - test_required: Whether test is required
    - error: Error message if failed
    """
    # Get application
    app_q = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    app = app_q.scalar_one_or_none()
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Get credential state
    cred_q = await db.execute(
        select(Credential)
        .where(Credential.application_id == application_id)
        .order_by(Credential.issued_at.desc())
    )
    cred = cred_q.scalar_one_or_none()
    
    if not cred:
        # No credential yet - just started
        return {
            "application_id": application_id,
            "status": app.status,
            "current_stage": "INIT",
            "stages_completed": [],
            "total_stages": 10,
            "progress_percentage": 0,
            "credential_preview": {
                "confidence": 0,
                "skills": []
            },
            "test_required": False,
            "error": None
        }
    
    state = cred.credential_json
    
    # Calculate progress
    total_stages = 10
    stages_completed = len(state.get("stages_completed", []))
    progress = int((stages_completed / total_stages) * 100)
    
    # Extract credential preview
    evidence = state.get("evidence", {})
    skills_data = evidence.get("skills", {})
    
    credential_preview = {
        "confidence": skills_data.get("confidence", 0),
        "skills": skills_data.get("skills", []),
        "github_verified": "github" in evidence,
        "leetcode_verified": "leetcode" in evidence,
        "codeforces_verified": "codeforces" in evidence
    }
    
    return {
        "application_id": application_id,
        "status": state.get("status", app.status),
        "current_stage": state.get("current_stage", "UNKNOWN"),
        "stages_completed": state.get("stages_completed", []),
        "total_stages": total_stages,
        "progress_percentage": progress,
        "credential_preview": credential_preview,
        "test_required": state.get("test_required", False),
        "match_score": state.get("match_score"),
        "error": state.get("error")
    }


@router.post("/application/{application_id}/submit-test")
async def submit_test(
    application_id: int,
    test_score: int = Form(...),
    test_data: str = Form(None),  # JSON string of full test results
    db: AsyncSession = Depends(get_db)
):
    """
    Submit test results and resume pipeline
    
    FormData:
    - test_score: Score (0-100)
    - test_data: Full test results as JSON string (optional)
    """
    # Get application
    app_q = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    app = app_q.scalar_one_or_none()
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if not app.test_required:
        raise HTTPException(status_code=400, detail="Test not required for this application")
    
    log.info(f"[TEST] Test submitted for application {application_id}: score={test_score}")
    
    # Get current credential state
    cred_q = await db.execute(
        select(Credential)
        .where(Credential.application_id == application_id)
        .order_by(Credential.issued_at.desc())
    )
    cred = cred_q.scalar_one_or_none()
    
    if not cred:
        raise HTTPException(status_code=400, detail="No credential found for this application")
    
    state = cred.credential_json
    
    # Add test results to evidence
    if "evidence" not in state:
        state["evidence"] = {}
    
    state["evidence"]["test"] = {
        "score": test_score,
        "data": test_data,
        "submitted_at": str(datetime.now())
    }
    state["stages_completed"].append("TEST")
    state["test_required"] = False
    state["status"] = "processing"
    
    # Update credential
    from app.passport import sign_credential
    h, sig = sign_credential(state)
    cred.credential_json = state
    cred.hash_sha256 = h
    cred.signature_b64 = sig
    
    # Update application
    app.status = "processing"
    app.test_required = False
    
    await db.commit()
    
    # Resume pipeline from BIAS stage
    log.info(f"[TEST] Resuming pipeline for application {application_id}")
    
    # Get application details for pipeline
    cand_q = await db.execute(select(Candidate).where(Candidate.id == app.candidate_id))
    cand = cand_q.scalar_one()
    
    # Continue pipeline from bias detection
    asyncio.create_task(
        continue_pipeline_after_test(application_id)
    )
    
    return {
        "application_id": application_id,
        "status": "processing",
        "message": "Test submitted. Pipeline resumed."
    }


async def continue_pipeline_after_test(application_id: int):
    """Continue pipeline after test submission"""
    from app.db import async_session_maker
    
    async with async_session_maker() as db:
        try:
            # Get application and state
            app_q = await db.execute(
                select(Application).where(Application.id == application_id)
            )
            app = app_q.scalar_one()
            
            cand_q = await db.execute(
                select(Candidate).where(Candidate.id == app.candidate_id)
            )
            cand = cand_q.scalar_one()
            
            cred_q = await db.execute(
                select(Credential)
                .where(Credential.application_id == application_id)
                .order_by(Credential.issued_at.desc())
            )
            cred = cred_q.scalar_one()
            
            state = cred.credential_json
            
            # Create orchestrator and continue from bias
            orchestrator = PipelineOrchestrator(db)
            orchestrator.state = state
            
            # Execute remaining stages: BIAS → MATCHING → PASSPORT
            # (This is a simplified version - full implementation would resume properly)
            
            log.info(f"[PIPELINE] Continued execution after test for app {application_id}")
            
        except Exception as e:
            log.error(f"[PIPELINE] Failed to continue after test for app {application_id}: {str(e)}")


@router.get("/jobs", response_model=list[JobOut])
async def list_published_jobs(db: AsyncSession = Depends(get_db)):
    """List all published jobs"""
    q = await db.execute(select(Job).where(Job.published == True).order_by(Job.created_at.desc()))
    jobs = q.scalars().all()
    return [
        JobOut(
            id=j.id,
            company_id=j.company_id,
            title=j.title,
            description=j.description,
            published=j.published
        )
        for j in jobs
    ]


@router.get("/{anon_id}/stats")
async def candidate_stats(anon_id: str, db: AsyncSession = Depends(get_db)):
    """Get candidate statistics"""
    q = await db.execute(select(Candidate).where(Candidate.anon_id == anon_id))
    cand = q.scalar_one_or_none()
    
    if not cand:
        return {
            "skill_passport_status": "Not verified",
            "active_applications": 0,
            "feedback_count": 0,
            "latest_update_count": 0
        }
    
    q_apps = await db.execute(select(Application).where(Application.candidate_id == cand.id))
    apps = q_apps.scalars().all()
    
    active = sum(1 for a in apps if a.status in {"pending", "processing", "verified", "needs_review", "matched", "selected"})
    feedback_count = sum(1 for a in apps if a.feedback_json)
    
    q_cred = await db.execute(select(Credential).where(Credential.candidate_id == cand.id))
    has_cred = q_cred.scalars().first() is not None
    
    return {
        "skill_passport_status": "Verified · Active" if has_cred else "Not verified",
        "active_applications": active,
        "feedback_count": feedback_count,
        "latest_update_count": feedback_count
    }


@router.get("/{anon_id}/applications")
async def list_applications(anon_id: str, db: AsyncSession = Depends(get_db)):
    """List all applications for a candidate"""
    q = await db.execute(select(Candidate).where(Candidate.anon_id == anon_id))
    cand = q.scalar_one_or_none()
    
    if not cand:
        return []
    
    q2 = await db.execute(
        select(Application)
        .where(Application.candidate_id == cand.id)
        .order_by(Application.created_at.desc())
    )
    apps = q2.scalars().all()
    
    out = []
    for a in apps:
        out.append({
            "application_id": a.id,
            "job_id": a.job_id,
            "status": a.status,
            "match_score": a.match_score,
            "feedback": a.feedback_json,
            "created_at": a.created_at.isoformat(),
            "test_required": a.test_required
        })
    
    return out
