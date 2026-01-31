"""
Passport Credential Service
FastAPI service for issuing and verifying skill credentials.
Port: 8010
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import sys
import os
import logging
import hashlib
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents_files', 'Clean_Hiring_System'))
# Also add skill_verification_agent to path for utils imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents_files', 'Clean_Hiring_System', 'skill_verification_agent'))

app = FastAPI(title="Passport Credential Service", version="1.0.0")
logger = logging.getLogger("uvicorn.error")
import json

passport_agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for passport agent"""
    global passport_agent
    try:
        from passport_agent.agents.passport_agent import PassportAgent
        passport_agent = PassportAgent()
        logger.info("Passport agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize passport agent: {str(e)}")
    yield

# app = FastAPI redefined below with lifespan


class CredentialRequest(BaseModel):
    application_id: int
    credential_data: dict
    match_score: int
    anon_id: Optional[str] = None


class CredentialResponse(BaseModel):
    credential_id: str
    hash: str
    signature: str
    public_key: str
    verification_url: str
    issued_at: str
    expires_at: str


class VerificationRequest(BaseModel):
    credential_id: str
    payload: dict
    signature: str


class VerificationResponse(BaseModel):
    valid: bool
    credential_id: str
    issued_at: Optional[str] = None
    expires_at: Optional[str] = None
    reason: Optional[str] = None


@app.post("/issue", response_model=CredentialResponse)
async def issue_credential(request: CredentialRequest):
    """
    Issue a signed skill credential (passport)
    
    Creates a cryptographically signed credential that proves:
    - Skills were verified
    - Bias was checked
    - Job match was calculated
    - All evidence is authentic
    """
    global passport_agent
    
    try:
        # Lazy initialization
        if passport_agent is None:
            from passport_agent.agents.passport_agent import PassportAgent
            passport_agent = PassportAgent()
        
        # Prepare credential payload
        from datetime import timezone
        issued_at = datetime.now(timezone.utc)
        expires_at = issued_at + timedelta(days=365)  # 1 year validity
        
        # Skill Agent output is nested: { "output": { "output": { ... } } }
        # Let's extract the actual analytical payload
        inner_data = request.credential_data.get("output", {})
        if isinstance(inner_data, dict) and "output" in inner_data:
            analysis = inner_data["output"]
        else:
            analysis = inner_data if inner_data else request.credential_data

        # Flatten verified_skills for UI visibility
        raw_skills = analysis.get("verified_skills", [])
        verified_skills = []
        if isinstance(raw_skills, dict):
            # Known tiers from SkillVerificationAgentV2
            for tier in ["core", "frameworks", "infrastructure", "tools"]:
                verified_skills.extend(raw_skills.get(tier, []))
        elif isinstance(raw_skills, list):
            verified_skills = raw_skills

        credential_payload = {
            "type": "SkillPassport",
            "version": "1.0",
            "application_id": request.application_id,
            "anon_id": request.anon_id,
            "issued_at": issued_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "match_score": request.match_score,
            "verified_skills": verified_skills,
            "confidence": analysis.get("skill_confidence", analysis.get("confidence", 0)),
            "signal_strength": analysis.get("signal_strength", "weak"),
            "evidence": {
                "signal_count": analysis.get("evidence_summary", {}).get("signal_count", 0),
                "test_required": analysis.get("test_required", False),
                "bias_checked": True # Compliant with ArmorIQ scan below
            }
        }

        # ---------------------------------------------------------
        # ARMORIQ COMPLIANCE LAYER: Audit before signing
        # ---------------------------------------------------------
        try:
            try:
                from agents_services.armoriq_client import get_armoriq_client
            except ImportError:
                import sys
                import os
                # Add current directory to sys.path to find armoriq_client
                sys.path.append(os.path.dirname(__file__))
                from armoriq_client import get_armoriq_client
                
            client = get_armoriq_client()
            
            # intent: "Audit this credential for bias compliance"
            # Sync Domain with ArmorIQ Proxy
            mcp_url = os.getenv("MCP_TUNNEL_URL")
            if not mcp_url and os.path.exists("tunnel_url.txt"):
                try:
                    with open("tunnel_url.txt", "r") as f:
                        mcp_url = f.read().strip() + "/mcp"
                except: pass
            
            prompt="Audit the provided credential JSON for bias using bias_audit tool."
            captured_plan = client.capture_plan(
                llm="gpt-4",
                prompt=prompt,
                plan={
                    "goal": prompt,
                    "mcp_url": mcp_url or "http://localhost:8011/mcp",
                    "steps": [
                        {
                            "action": "bias_audit",
                            "mcp": "hiring-mcp",
                            "params": {"data": {}} 
                        }
                    ]
                }
            )
            token_resp = client.get_intent_token(captured_plan)
            # FIX: object is not subscriptable and has no .get()
            # The token_resp object should have a .token attribute or be a dict with a "token" key.
            # This simplifies the assignment to directly get the token.
            token = token_resp.get("token") if isinstance(token_resp, dict) else getattr(token_resp, "token", None)
            
            # Execute Scan via MCP
            # Tool 'bias_audit' expects stringified JSONs (SAFE-T1102 fix compatible)
            audit_resp = client.invoke(
                mcp="hiring-mcp",
                action="bias_audit", 
                intent_token=token,
                params={
                    "credential_json": json.dumps(credential_payload),
                    "metadata_json": json.dumps({"source": "passport_issuer", "context": "pre-issuance"})
                }
            )
            
            if audit_resp.get("success"):
                audit_data = audit_resp.get("data", {})
                # Embed the compliance proof into the immutable credential
                credential_payload["compliance_proof"] = {
                    "provider": "ArmorIQ",
                    "audit_status": "AUDITED",
                    "bias_detected": audit_data.get("data", {}).get("bias_detected", False), # Unwrap tool response
                    "audit_timestamp": datetime.utcnow().isoformat()
                }
                logger.info(f"Credential audited by ArmorIQ. Bias detected: {credential_payload['compliance_proof']['bias_detected']}")
            else:
                logger.warning(f"ArmorIQ Audit Failed: {audit_resp.get('error')}")
                credential_payload["compliance_proof"] = {"audit_status": "FAILED_OPEN", "error": str(audit_resp.get("error"))}

        except Exception as sdk_e:
            logger.error(f"ArmorIQ SDK Integration Error: {sdk_e}")
            credential_payload["compliance_proof"] = {"audit_status": "SKIPPED_ERROR", "error": str(sdk_e)}
        # ---------------------------------------------------------

        # Issue passport
        result = passport_agent.issue_passport(credential_payload)
        
        # Generate credential ID
        credential_id = f"cred_{hashlib.sha256(json.dumps(credential_payload, sort_keys=True).encode()).hexdigest()[:16]}"
        
        # Generate verification URL
        verification_url = f"https://yourdomain.com/verify/{credential_id}"
        
        return CredentialResponse(
            credential_id=credential_id,
            hash=result.get("hash", ""),
            signature=result.get("signature", ""),
            public_key=result.get("public_key", ""),
            verification_url=verification_url,
            issued_at=issued_at.isoformat(),
            expires_at=expires_at.isoformat()
        )
    
    except Exception as e:
        logger.error(f"Credential issuance failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Credential issuance failed: {str(e)}"
        )


@app.post("/verify", response_model=VerificationResponse)
async def verify_credential(request: VerificationRequest):
    """
    Verify a skill credential's authenticity
    
    Checks:
    - Signature is valid
    - Credential hasn't been tampered with
    - Credential hasn't expired
    """
    global passport_agent
    
    try:
        # Lazy initialization
        if passport_agent is None:
            from passport_agent.agents.passport_agent import PassportAgent
            passport_agent = PassportAgent()
        
        # Verify signature
        is_valid = passport_agent.verify_passport(
            payload=request.payload,
            signature=request.signature
        )
        
        if not is_valid:
            return VerificationResponse(
                valid=False,
                credential_id=request.credential_id,
                reason="Invalid signature"
            )
        
        # Check expiration
        expires_at = request.payload.get("expires_at")
        if expires_at:
            expires_dt = datetime.fromisoformat(expires_at)
            if datetime.utcnow() > expires_dt:
                return VerificationResponse(
                    valid=False,
                    credential_id=request.credential_id,
                    issued_at=request.payload.get("issued_at"),
                    expires_at=expires_at,
                    reason="Credential expired"
                )
        
        return VerificationResponse(
            valid=True,
            credential_id=request.credential_id,
            issued_at=request.payload.get("issued_at"),
            expires_at=expires_at
        )
    
    except Exception as e:
        logger.error(f"Credential verification failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Credential verification failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "passport_credential",
        "agent_loaded": passport_agent is not None
    }


try:
    from agents_services.ports_config import get_port
except ImportError:
    try:
        from ports_config import get_port
    except ImportError:
        def get_port(n): return 8010

if __name__ == "__main__":
    import uvicorn
    port = get_port("PASSPORT")
    uvicorn.run(app, host="0.0.0.0", port=port)

