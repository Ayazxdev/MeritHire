from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import Company, Job, Application, Candidate, Credential, AgentRun, ReviewCase, Blacklist
from app.schemas import CreateCompany, CreateJob
from app.audit import log_event
from app.agent_client import call_match_agent
from sqlalchemy import select, func
from fastapi import HTTPException
from app.schemas import JobOut

router = APIRouter(prefix="/company", tags=["company"])

@router.post("/create")
async def create_company(payload: CreateCompany, db: AsyncSession = Depends(get_db)):
    c = Company(name=payload.name)
    db.add(c)
    await db.commit()
    await db.refresh(c)
    await log_event(db, "company", "company_created", {"company_id": c.id})
    return {"company_id": c.id}

@router.post("/job")
async def create_job(payload: CreateJob, db: AsyncSession = Depends(get_db)):

    # Lightweight fairness scan (demo-safe): block common biased terms.
    biased_terms = ["rockstar", "ninja", "digital native", "young", "fresh blood", "ivy league", "top-tier university"]
    findings = [t for t in biased_terms if t.lower() in (payload.description or "").lower()]
    if findings:
        raise HTTPException(status_code=400, detail=f"Job description contains potentially biased language: {', '.join(findings)}")

    job = Job(company_id=payload.company_id, title=payload.title, description=payload.description, published=payload.published, max_participants=payload.max_participants)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    await log_event(db, "company", "job_created", {"job_id": job.id})
    return {"job_id": job.id, "published": job.published}

@router.get("/{company_id}/jobs", response_model=list[JobOut])
async def list_company_jobs(company_id: int, db: AsyncSession = Depends(get_db)):
    # Return jobs with aggregated application counts for dashboard cards.
    q = await db.execute(
        select(
            Job,
            func.count(Application.id).label("candidates_count"),
        )
        .outerjoin(Application, Application.job_id == Job.id)
        .where(Job.company_id == company_id)
        .group_by(Job.id)
        .order_by(Job.id.desc())
    )
    rows = q.all()
    out = []
    for job, cand_count in rows:
        out.append(
            JobOut(
                id=job.id,
                company_id=job.company_id,
                title=job.title,
                description=job.description,
                published=job.published,
                max_participants=getattr(job, "max_participants", None),
                application_deadline=getattr(job, "application_deadline", None),
                fairness_status=getattr(job, "fairness_status", "VERIFIED") or "VERIFIED",
                candidates_count=int(cand_count or 0),
            )
        )
    return out


@router.get("/{company_id}/stats")
async def company_stats(company_id: int, db: AsyncSession = Depends(get_db)):
    q_jobs = await db.execute(select(Job).where(Job.company_id == company_id, Job.published == True))
    jobs = q_jobs.scalars().all()
    active_roles = len(jobs)

    # candidates in flow = distinct candidates across all apps for this company's jobs
    job_ids = [j.id for j in jobs]
    if not job_ids:
        return {"active_roles": 0, "candidates_in_flow": 0, "fairness_status": "VERIFIED"}
    q_apps = await db.execute(select(Application.candidate_id).where(Application.job_id.in_(job_ids)).distinct())
    candidates_in_flow = len(q_apps.scalars().all())
    return {"active_roles": active_roles, "candidates_in_flow": candidates_in_flow, "fairness_status": "VERIFIED"}


@router.post("/{company_id}/jobs/{job_id}/run-matching")
async def run_matching(company_id: int, job_id: int, db: AsyncSession = Depends(get_db)):
    # Fetch job
    qj = await db.execute(select(Job).where(Job.id == job_id, Job.company_id == company_id))
    job = qj.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Pull verified applications
    qa = await db.execute(select(Application).where(Application.job_id == job_id))
    apps = qa.scalars().all()
    if not apps:
        return {"selected": 0, "total": 0}

    # Build a simple per-candidate match payload based on latest credential for that application
    # If external matching agent is unavailable, fall back to confidence score.
    scored = []
    for a in apps:
        qc = await db.execute(select(Credential).where(Credential.application_id == a.id).order_by(Credential.issued_at.desc()))
        cred = qc.scalars().first()
        if not cred:
            continue
        payload = {"credential": cred.credential_json, "job_description": {"title": job.title, "description": job.description}}
        try:
            res = await call_match_agent(payload)
            score = int(res.get("match_score", res.get("output", {}).get("match_score", 0)) or 0)
            breakdown = res.get("breakdown") or res.get("output", {}).get("breakdown")
        except Exception:
            score = int(cred.credential_json.get("confidence", 0))
            breakdown = None
        scored.append((a, score, breakdown))

    scored.sort(key=lambda t: t[1], reverse=True)
    k = job.max_participants or 5
    selected = set(x[0].id for x in scored[:k])

    for a, score, breakdown in scored:
        a.match_score = score
        if a.id in selected:
            a.status = "selected"
            a.feedback_json = {"message": "You are selected. The company will contact you shortly.", "breakdown": breakdown}
        else:
            a.status = "rejected"
            a.feedback_json = {"message": "Not selected this time. Here is developmental feedback.", "breakdown": breakdown}

    await db.commit()
    await log_event(db, "company", "matching_run", {"job_id": job_id, "selected": len(selected), "total": len(scored)})
    return {"selected": len(selected), "total": len(scored)}


@router.get("/{company_id}/jobs/{job_id}/selected")
async def list_selected(company_id: int, job_id: int, db: AsyncSession = Depends(get_db)):
    qj = await db.execute(select(Job).where(Job.id == job_id, Job.company_id == company_id))
    job = qj.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    q = await db.execute(
        select(Application, Candidate)
        .join(Candidate, Application.candidate_id == Candidate.id)
        .where(Application.job_id == job_id, Application.status == "selected")
        .order_by(Application.match_score.desc().nullslast())
    )
    rows = q.all()
    return [{"anon_id": cand.anon_id, "match_score": app.match_score or 0, "breakdown": (app.feedback_json or {}).get("breakdown")} for app, cand in rows]



@router.get("/{company_id}/jobs/{job_id}/applications")
async def list_job_applications(company_id: int, job_id: int, db: AsyncSession = Depends(get_db)):
    # Verify job belongs to company
    qj = await db.execute(select(Job).where(Job.id == job_id, Job.company_id == company_id))
    job = qj.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    q = await db.execute(
        select(Application, Candidate)
        .join(Candidate, Application.candidate_id == Candidate.id)
        .where(Application.job_id == job_id)
        .order_by(Application.created_at.desc())
    )
    rows = q.all()
    # Defensive de-dup: keep the most recent application per candidate for this job
    out = []
    seen_candidate_ids = set()
    for app, cand in rows:
        if cand.id in seen_candidate_ids:
            continue
        seen_candidate_ids.add(cand.id)
        out.append({
            "application_id": app.id,
            "anon_id": cand.anon_id,
            "status": app.status,
            "match_score": app.match_score,
            "feedback": app.feedback_json,
            "created_at": app.created_at.isoformat() if app.created_at else None,
        })
    return out


@router.get("/{company_id}/review-queue")
async def review_queue(company_id: int, db: AsyncSession = Depends(get_db)):
    # company sees review cases for jobs they own
    q = await db.execute(
        select(ReviewCase, Candidate, Application, Job)
        .join(Application, ReviewCase.application_id == Application.id)
        .join(Job, Application.job_id == Job.id)
        .join(Candidate, ReviewCase.candidate_id == Candidate.id)
        .where(Job.company_id == company_id, ReviewCase.status == "pending")
        .order_by(ReviewCase.created_at.desc())
    )
    rows = q.all()
    out = []
    for rc, cand, app, job in rows:
        out.append({
            "id": rc.id,
            "application_id": rc.application_id,
            "job_id": rc.job_id,
            "candidate_anon_id": cand.anon_id,
            "severity": rc.severity,
            "reason": rc.reason,
            "status": rc.status,
            "created_at": rc.created_at.isoformat(),
        })
    return out


@router.post("/{company_id}/review-queue/{case_id}/action")
async def review_action(company_id: int, case_id: int, payload: dict, db: AsyncSession = Depends(get_db)):
    action = payload.get("action")
    note = payload.get("note") or ""

    q = await db.execute(select(ReviewCase).where(ReviewCase.id == case_id))
    rc = q.scalar_one_or_none()
    if not rc:
        raise HTTPException(status_code=404, detail="Case not found")

    # Ensure case belongs to this company via job ownership
    qj = await db.execute(select(Job).where(Job.id == rc.job_id, Job.company_id == company_id))
    if not qj.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not allowed")

    if action == "clear":
        rc.status = "cleared"
        # Mark application as verified so it can proceed
        qa = await db.execute(select(Application).where(Application.id == rc.application_id))
        app = qa.scalar_one_or_none()
        if app and app.status == "needs_review":
            app.status = "verified"
    elif action == "blacklist":
        rc.status = "blacklisted"
        # Add to blacklist and reject application
        qa = await db.execute(select(Application).where(Application.id == rc.application_id))
        app = qa.scalar_one_or_none()
        if app:
            app.status = "rejected"
        qb = await db.execute(select(Blacklist).where(Blacklist.candidate_id == rc.candidate_id))
        if not qb.scalar_one_or_none():
            db.add(Blacklist(candidate_id=rc.candidate_id, reason=note or rc.reason))
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use clear|blacklist")

    await db.commit()
    await log_event(db, "company", "review_action", {"case_id": case_id, "action": action})
    return {"ok": True}
