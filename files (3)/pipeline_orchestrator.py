"""
Pipeline Orchestrator
Manages the complete 10-stage agent pipeline execution
"""
import logging
import httpx
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Application, Candidate, Job, AgentRun, Credential, ReviewCase, Blacklist
from app.passport import sign_credential
from datetime import datetime

log = logging.getLogger("uvicorn.error")

class PipelineOrchestrator:
    """Orchestrates the complete agent pipeline"""
    
    # Agent service URLs
    SERVICES = {
        "ATS": "http://localhost:8004",
        "GITHUB": "http://localhost:8005",
        "LEETCODE": "http://localhost:8006",
        "CODEFORCES": "http://localhost:8007",
        "LINKEDIN": "http://localhost:8008",
        "SKILL": "http://localhost:8001",
        "TEST": "http://localhost:8009",
        "BIAS": "http://localhost:8002",
        "MATCHING": "http://localhost:8003",
        "PASSPORT": "http://localhost:8010",
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.state: Dict[str, Any] = {}
    
    async def call_agent(self, service_name: str, endpoint: str, payload: Dict) -> Dict:
        """Call an agent service and return result"""
        url = f"{self.SERVICES[service_name]}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                log.info(f"[PIPELINE] Calling {service_name}: {url}")
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                log.info(f"[PIPELINE] {service_name} completed successfully")
                return result
        except httpx.HTTPError as e:
            log.error(f"[PIPELINE] {service_name} failed: {str(e)}")
            raise
        except Exception as e:
            log.error(f"[PIPELINE] {service_name} unexpected error: {str(e)}")
            raise
    
    async def log_agent_run(
        self,
        application_id: int,
        agent_name: str,
        input_payload: Dict,
        output_payload: Optional[Dict] = None,
        status: str = "queued"
    ) -> AgentRun:
        """Log an agent run to the database"""
        run = AgentRun(
            application_id=application_id,
            agent_name=agent_name,
            input_payload=input_payload,
            output_payload=output_payload,
            status=status
        )
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run
    
    async def save_credential_state(self, application_id: int, state: Dict):
        """Save or update credential state"""
        # Check if credential exists
        q = await self.db.execute(
            select(Credential)
            .where(Credential.application_id == application_id)
            .order_by(Credential.issued_at.desc())
        )
        cred = q.scalar_one_or_none()
        
        # Get application for candidate_id
        app_q = await self.db.execute(
            select(Application).where(Application.id == application_id)
        )
        app = app_q.scalar_one()
        
        if cred:
            # Update existing
            cred.credential_json = state
            h, sig = sign_credential(state)
            cred.hash_sha256 = h
            cred.signature_b64 = sig
        else:
            # Create new
            h, sig = sign_credential(state)
            cred = Credential(
                candidate_id=app.candidate_id,
                application_id=application_id,
                credential_json=state,
                hash_sha256=h,
                signature_b64=sig
            )
            self.db.add(cred)
        
        await self.db.commit()
        return cred
    
    async def execute_pipeline(
        self,
        application_id: int,
        resume_text: str,
        resume_path: str,
        github_url: Optional[str],
        leetcode_url: Optional[str],
        codeforces_url: Optional[str],
        linkedin_pdf_path: Optional[str],
        linkedin_text: Optional[str]
    ) -> Dict:
        """
        Execute the complete 10-stage pipeline
        
        Returns pipeline state or raises exception on critical failure
        """
        # Get application and candidate
        app_q = await self.db.execute(
            select(Application).where(Application.id == application_id)
        )
        app = app_q.scalar_one()
        
        cand_q = await self.db.execute(
            select(Candidate).where(Candidate.id == app.candidate_id)
        )
        cand = cand_q.scalar_one()
        
        # Initialize state
        self.state = {
            "application_id": application_id,
            "job_id": app.job_id,
            "status": "processing",
            "current_stage": "INIT",
            "stages_completed": [],
            "evidence": {},
            "flags": [],
            "test_required": False,
            "credential_status": "INIT"
        }
        
        # Save initial state
        await self.save_credential_state(application_id, self.state)
        
        try:
            # ============================================================
            # STAGE 1: ATS (FRAUD DETECTION)
            # ============================================================
            log.info(f"[PIPELINE] Stage 1: ATS - application_id={application_id}")
            self.state["current_stage"] = "ATS"
            app.status = "processing"
            await self.db.commit()
            
            ats_input = {
                "application_id": application_id,
                "resume_text": resume_text,
                "resume_path": resume_path
            }
            
            run = await self.log_agent_run(application_id, "ATS", ats_input)
            
            try:
                ats_result = await self.call_agent("ATS", "/run", ats_input)
                run.output_payload = ats_result
                run.status = "ok"
                
                self.state["evidence"]["ats"] = ats_result
                
                # Check for blacklist
                if ats_result.get("action") == "BLACKLIST":
                    log.warning(f"[PIPELINE] ATS blacklisted application {application_id}")
                    
                    # Blacklist candidate
                    blacklist = Blacklist(
                        candidate_id=app.candidate_id,
                        reason=ats_result.get("reason", "ATS fraud detection")
                    )
                    self.db.add(blacklist)
                    
                    app.status = "rejected"
                    self.state["status"] = "rejected"
                    self.state["credential_status"] = "REJECTED"
                    
                    await self.db.commit()
                    await self.save_credential_state(application_id, self.state)
                    
                    return self.state
                
                # Check for review
                if ats_result.get("action") == "NEEDS_REVIEW":
                    log.info(f"[PIPELINE] ATS flagged application {application_id} for review")
                    
                    review = ReviewCase(
                        application_id=application_id,
                        job_id=app.job_id,
                        candidate_id=app.candidate_id,
                        triggered_by="ATS",
                        severity=ats_result.get("severity", "medium"),
                        reason=ats_result.get("reason", "ATS flagged for review"),
                        evidence=ats_result
                    )
                    self.db.add(review)
                    
                    app.status = "needs_review"
                    self.state["status"] = "needs_review"
                    
                    await self.db.commit()
                    await self.save_credential_state(application_id, self.state)
                    
                    return self.state
                
                self.state["stages_completed"].append("ATS")
                
            except Exception as e:
                run.status = "failed"
                run.output_payload = {"error": str(e)}
                log.error(f"[PIPELINE] ATS failed: {str(e)}")
                # Continue pipeline with partial evidence
            
            await self.db.commit()
            
            # ============================================================
            # STAGE 2: GITHUB
            # ============================================================
            if github_url:
                log.info(f"[PIPELINE] Stage 2: GitHub - application_id={application_id}")
                self.state["current_stage"] = "GITHUB"
                await self.save_credential_state(application_id, self.state)
                
                github_input = {
                    "github_url": github_url,
                    "application_id": application_id
                }
                
                run = await self.log_agent_run(application_id, "GITHUB", github_input)
                
                try:
                    github_result = await self.call_agent("GITHUB", "/scrape", github_input)
                    run.output_payload = github_result
                    run.status = "ok"
                    
                    self.state["evidence"]["github"] = github_result
                    self.state["stages_completed"].append("GITHUB")
                    
                except Exception as e:
                    run.status = "failed"
                    run.output_payload = {"error": str(e)}
                    log.error(f"[PIPELINE] GitHub failed: {str(e)}")
                
                await self.db.commit()
            
            # ============================================================
            # STAGE 3: LEETCODE
            # ============================================================
            if leetcode_url:
                log.info(f"[PIPELINE] Stage 3: LeetCode - application_id={application_id}")
                self.state["current_stage"] = "LEETCODE"
                await self.save_credential_state(application_id, self.state)
                
                leetcode_input = {
                    "leetcode_url": leetcode_url,
                    "application_id": application_id
                }
                
                run = await self.log_agent_run(application_id, "LEETCODE", leetcode_input)
                
                try:
                    leetcode_result = await self.call_agent("LEETCODE", "/scrape", leetcode_input)
                    run.output_payload = leetcode_result
                    run.status = "ok"
                    
                    self.state["evidence"]["leetcode"] = leetcode_result
                    self.state["stages_completed"].append("LEETCODE")
                    
                except Exception as e:
                    run.status = "failed"
                    run.output_payload = {"error": str(e)}
                    log.error(f"[PIPELINE] LeetCode failed: {str(e)}")
                
                await self.db.commit()
            
            # ============================================================
            # STAGE 4: CODEFORCES
            # ============================================================
            if codeforces_url:
                log.info(f"[PIPELINE] Stage 4: Codeforces - application_id={application_id}")
                self.state["current_stage"] = "CODEFORCES"
                await self.save_credential_state(application_id, self.state)
                
                codeforces_input = {
                    "codeforces_url": codeforces_url,
                    "application_id": application_id
                }
                
                run = await self.log_agent_run(application_id, "CODEFORCES", codeforces_input)
                
                try:
                    codeforces_result = await self.call_agent("CODEFORCES", "/scrape", codeforces_input)
                    run.output_payload = codeforces_result
                    run.status = "ok"
                    
                    self.state["evidence"]["codeforces"] = codeforces_result
                    self.state["stages_completed"].append("CODEFORCES")
                    
                except Exception as e:
                    run.status = "failed"
                    run.output_payload = {"error": str(e)}
                    log.error(f"[PIPELINE] Codeforces failed: {str(e)}")
                
                await self.db.commit()
            
            # ============================================================
            # STAGE 5: LINKEDIN
            # ============================================================
            if linkedin_pdf_path and linkedin_text:
                log.info(f"[PIPELINE] Stage 5: LinkedIn - application_id={application_id}")
                self.state["current_stage"] = "LINKEDIN"
                await self.save_credential_state(application_id, self.state)
                
                linkedin_input = {
                    "linkedin_text": linkedin_text,
                    "linkedin_path": linkedin_pdf_path,
                    "application_id": application_id
                }
                
                run = await self.log_agent_run(application_id, "LINKEDIN", linkedin_input)
                
                try:
                    linkedin_result = await self.call_agent("LINKEDIN", "/parse", linkedin_input)
                    run.output_payload = linkedin_result
                    run.status = "ok"
                    
                    self.state["evidence"]["linkedin"] = linkedin_result
                    self.state["stages_completed"].append("LINKEDIN")
                    
                except Exception as e:
                    run.status = "failed"
                    run.output_payload = {"error": str(e)}
                    log.error(f"[PIPELINE] LinkedIn failed: {str(e)}")
                
                await self.db.commit()
            
            # ============================================================
            # STAGE 6: SKILL VERIFICATION
            # ============================================================
            log.info(f"[PIPELINE] Stage 6: Skill Verification - application_id={application_id}")
            self.state["current_stage"] = "SKILL"
            await self.save_credential_state(application_id, self.state)
            
            skill_input = {
                "application_id": application_id,
                "resume_text": resume_text,
                "github_url": github_url,
                "leetcode_url": leetcode_url,
                "codeforces_url": codeforces_url,
                "linkedin_url": linkedin_pdf_path,
                "anon_id": cand.anon_id,
                "evidence": self.state["evidence"]
            }
            
            run = await self.log_agent_run(application_id, "SKILL", skill_input)
            
            skill_result = await self.call_agent("SKILL", "/run", skill_input)
            run.output_payload = skill_result
            run.status = "ok"
            
            self.state["evidence"]["skills"] = skill_result.get("output", {})
            self.state["stages_completed"].append("SKILL")
            
            # Check if test required
            if skill_result.get("output", {}).get("test_required"):
                log.info(f"[PIPELINE] Test required for application {application_id}")
                
                app.test_required = True
                app.status = "test_required"
                self.state["status"] = "test_required"
                self.state["test_required"] = True
                self.state["credential_status"] = "PENDING_TEST"
                
                await self.db.commit()
                await self.save_credential_state(application_id, self.state)
                
                return self.state
            
            await self.db.commit()
            
            # ============================================================
            # STAGE 7: CONDITIONAL TEST
            # ============================================================
            # This stage is handled separately when user submits test
            # We skip it here as no test is required
            
            # ============================================================
            # STAGE 8: BIAS DETECTION
            # ============================================================
            log.info(f"[PIPELINE] Stage 8: Bias Detection - application_id={application_id}")
            self.state["current_stage"] = "BIAS"
            await self.save_credential_state(application_id, self.state)
            
            bias_input = {
                "credential": self.state["evidence"],
                "metadata": {
                    "gender": cand.gender or "unknown",
                    "college": cand.college or "unknown"
                },
                "mode": "realtime"
            }
            
            run = await self.log_agent_run(application_id, "BIAS", bias_input)
            
            try:
                bias_result = await self.call_agent("BIAS", "/run", bias_input)
                run.output_payload = bias_result
                run.status = "ok"
                
                self.state["evidence"]["bias"] = bias_result
                
                # Check for high/critical severity
                if bias_result.get("severity") in ["high", "critical"]:
                    log.warning(f"[PIPELINE] Bias detected (severity={bias_result.get('severity')})")
                    
                    review = ReviewCase(
                        application_id=application_id,
                        job_id=app.job_id,
                        candidate_id=app.candidate_id,
                        triggered_by="BIAS",
                        severity=bias_result.get("severity"),
                        reason="Bias detection flagged systemic issues",
                        evidence=bias_result
                    )
                    self.db.add(review)
                    # Note: Don't stop pipeline for bias
                
                self.state["stages_completed"].append("BIAS")
                
            except Exception as e:
                run.status = "failed"
                run.output_payload = {"error": str(e)}
                log.error(f"[PIPELINE] Bias detection failed: {str(e)}")
            
            await self.db.commit()
            
            # ============================================================
            # STAGE 9: MATCHING
            # ============================================================
            log.info(f"[PIPELINE] Stage 9: Matching - application_id={application_id}")
            self.state["current_stage"] = "MATCHING"
            await self.save_credential_state(application_id, self.state)
            
            # Get job details
            job_q = await self.db.execute(
                select(Job).where(Job.id == app.job_id)
            )
            job = job_q.scalar_one()
            
            matching_input = {
                "credential": self.state["evidence"],
                "job_description": {
                    "title": job.title,
                    "description": job.description,
                    "required_skills": [],  # TODO: Parse from job
                    "preferred_skills": []
                }
            }
            
            run = await self.log_agent_run(application_id, "MATCHING", matching_input)
            
            matching_result = await self.call_agent("MATCHING", "/run", matching_input)
            run.output_payload = matching_result
            run.status = "ok"
            
            self.state["evidence"]["matching"] = matching_result
            self.state["match_score"] = matching_result.get("match_score", 0)
            app.match_score = matching_result.get("match_score", 0)
            app.feedback_json = {
                "matched_skills": matching_result.get("matched_skills", []),
                "missing_skills": matching_result.get("missing_skills", []),
                "recommendation": matching_result.get("recommendation", "")
            }
            
            self.state["stages_completed"].append("MATCHING")
            
            await self.db.commit()
            
            # ============================================================
            # STAGE 10: PASSPORT ISSUANCE
            # ============================================================
            log.info(f"[PIPELINE] Stage 10: Passport Issuance - application_id={application_id}")
            self.state["current_stage"] = "PASSPORT"
            await self.save_credential_state(application_id, self.state)
            
            passport_input = {
                "application_id": application_id,
                "credential_data": self.state["evidence"],
                "match_score": self.state["match_score"]
            }
            
            run = await self.log_agent_run(application_id, "PASSPORT", passport_input)
            
            passport_result = await self.call_agent("PASSPORT", "/issue", passport_input)
            run.output_payload = passport_result
            run.status = "ok"
            
            self.state["evidence"]["passport"] = passport_result
            self.state["stages_completed"].append("PASSPORT")
            
            await self.db.commit()
            
            # ============================================================
            # FINALIZE
            # ============================================================
            self.state["status"] = "completed"
            self.state["current_stage"] = "COMPLETE"
            self.state["credential_status"] = "VERIFIED"
            
            # Set final application status
            if self.state["match_score"] >= 60:
                app.status = "matched"
            else:
                app.status = "rejected"
            
            await self.db.commit()
            await self.save_credential_state(application_id, self.state)
            
            log.info(f"[PIPELINE] Pipeline completed for application {application_id}")
            
            return self.state
            
        except Exception as e:
            log.error(f"[PIPELINE] Pipeline failed: {str(e)}")
            
            app.status = "failed"
            self.state["status"] = "failed"
            self.state["error"] = str(e)
            
            await self.db.commit()
            await self.save_credential_state(application_id, self.state)
            
            raise
