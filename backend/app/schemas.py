from pydantic import BaseModel, Field
from typing import Optional, Any
import datetime

# -----------------
# Auth
# -----------------
class CreateCompany(BaseModel):
    name: str

class CandidateSignup(BaseModel):
    email: str
    password: str
    name: Optional[str] = None
    gender: Optional[str] = None
    college: Optional[str] = None
    engineer_level: Optional[str] = None  # e.g. intern/junior/mid/senior

class CandidateLogin(BaseModel):
    email: str
    password: str

class CandidateAuthResponse(BaseModel):
    candidate_id: int
    anon_id: str
    # kept for debugging / audit; frontend can ignore
    email: str

class CompanySignup(BaseModel):
    name: str
    email: str
    password: str

class CompanyLogin(BaseModel):
    email: str
    password: str

class CompanyAuthResponse(BaseModel):
    company_id: int
    name: str
    # kept for debugging / audit; frontend can ignore
    email: str

# -----------------
# Jobs
# -----------------
class CreateJob(BaseModel):
    company_id: int
    title: str
    description: str
    published: bool = True
    max_participants: Optional[int] = None
    application_deadline: Optional[str] = None  # ISO date string from UI

class JobOut(BaseModel):
    id: int
    company_id: int
    title: str
    description: str
    published: bool

    # Optional/extended fields used by dashboards
    max_participants: int | None = None
    application_deadline: datetime.datetime | None = None
    fairness_status: str = "VERIFIED"
    candidates_count: int = 0

class ApplyRequest(BaseModel):
    job_id: int
    anon_id: str
    resume_text: str
    github_url: Optional[str] = None
    leetcode_url: Optional[str] = None
    codeforces_url: Optional[str] = None
    linkedin_url: Optional[str] = None

# -----------------
# Agents / Passport
# -----------------
class AgentOutput(BaseModel):
    output: dict
    explanation: Optional[str] = None
    flags: list[str] = Field(default_factory=list)

class PassportResponse(BaseModel):
    anon_id: str
    credential: dict
    hash_sha256: str
    signature_b64: str
    public_key_b64: str

# -----------------
# Review / Pipeline (v2)
# -----------------
class ReviewCaseOut(BaseModel):
    id: int
    application_id: int
    job_id: int
    candidate_anon_id: str
    severity: str
    reason: str
    status: str
    created_at: str

class ReviewAction(BaseModel):
    action: str = Field(..., description="clear|blacklist")
    note: Optional[str] = None

class SelectedCandidateOut(BaseModel):
    anon_id: str
    match_score: int
    breakdown: Optional[dict] = None

class CandidateStatsOut(BaseModel):
    skill_passport_status: str
    active_applications: int
    feedback_count: int
    latest_update_count: int

class CompanyStatsOut(BaseModel):
    active_roles: int
    candidates_in_flow: int
    fairness_status: str
