from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import secrets

from app.db import get_db
from app.models import Candidate, Company
from app.schemas import (
    CandidateSignup, CandidateLogin, CandidateAuthResponse,
    CompanySignup, CompanyLogin, CompanyAuthResponse
)
from app.auth_utils import hash_password, verify_password
from app.audit import log_event

router = APIRouter(prefix="/auth", tags=["auth"])

def _new_anon_id() -> str:
    return "ANON-" + secrets.token_hex(6).upper()

@router.post("/candidate/signup", response_model=CandidateAuthResponse)
async def candidate_signup(
    payload: CandidateSignup,
    db: AsyncSession = Depends(get_db),
):
    q = await db.execute(
        select(Candidate).where(Candidate.email == payload.email.lower().strip())
    )
    if q.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    try:
        pw_hash = hash_password(payload.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    cand = Candidate(
        anon_id=_new_anon_id(),
        email=payload.email.lower().strip(),
        password_hash=pw_hash,  # ✅ use computed hash
        name=payload.name,
        gender=payload.gender,
        college=payload.college,
        engineer_level=payload.engineer_level,
    )

    db.add(cand)
    await db.commit()
    await db.refresh(cand)

    await log_event(
        db,
        "candidate",
        "candidate_signup",
        {"candidate_id": cand.id, "anon_id": cand.anon_id},
    )

    return CandidateAuthResponse(
        candidate_id=cand.id,
        anon_id=cand.anon_id,
        email=cand.email,
    )

@router.post("/candidate/login", response_model=CandidateAuthResponse)
async def candidate_login(payload: CandidateLogin, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(Candidate).where(Candidate.email == payload.email.lower().strip()))
    cand = q.scalar_one_or_none()
    if not cand or not verify_password(payload.password, cand.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    await log_event(db, "candidate", "candidate_login", {"candidate_id": cand.id, "anon_id": cand.anon_id})
    return CandidateAuthResponse(candidate_id=cand.id, anon_id=cand.anon_id, email=cand.email)

@router.post("/company/signup", response_model=CompanyAuthResponse)
async def company_signup(
    payload: CompanySignup,
    db: AsyncSession = Depends(get_db),
):
    q = await db.execute(
        select(Company).where(Company.email == payload.email.lower().strip())
    )
    if q.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")
    try:
        pw_hash = hash_password(payload.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    c = Company(
        name=payload.name,
        email=payload.email.lower().strip(),
        password_hash=pw_hash,
    )
    db.add(c)
    await db.commit()
    await db.refresh(c)
    await log_event(db, "company", "company_signup", {"company_id": c.id})
    return CompanyAuthResponse(
        company_id=c.id,
        name=c.name,
        email=c.email,
    )

@router.post("/company/login", response_model=CompanyAuthResponse)
async def company_login(payload: CompanyLogin, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(Company).where(Company.email == payload.email.lower().strip()))
    c = q.scalar_one_or_none()
    if not c or not verify_password(payload.password, c.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    await log_event(db, "company", "company_login", {"company_id": c.id})
    return CompanyAuthResponse(company_id=c.id, name=c.name, email=c.email)
