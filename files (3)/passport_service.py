"""
Passport Issuance Service
Port: 8010

Issues final skill credential/passport with:
- Credential ID
- Hash
- Signature
- Verification URL
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import hashlib
import base64
import json
from datetime import datetime

app = FastAPI(title="Passport Issuance Service", version="1.0.0")

class PassportRequest(BaseModel):
    application_id: int
    credential_data: dict
    match_score: int

class PassportResponse(BaseModel):
    credential_id: str
    hash: str
    signature: str
    verification_url: str
    issued_at: str

@app.post("/issue", response_model=PassportResponse)
async def issue_passport(request: PassportRequest):
    """
    Issue final skill passport credential
    """
    try:
        # Create credential ID
        credential_id = f"CRED-{request.application_id}-{int(datetime.now().timestamp())}"
        
        # Prepare credential document
        credential_doc = {
            "id": credential_id,
            "type": "SkillCredential",
            "application_id": request.application_id,
            "issued_at": datetime.now().isoformat(),
            "match_score": request.match_score,
            "verified_data": {
                "skills": request.credential_data.get("skills", {}).get("skills", []),
                "confidence": request.credential_data.get("skills", {}).get("confidence", 0),
                "evidence_sources": {
                    "ats": "ats" in request.credential_data,
                    "github": "github" in request.credential_data,
                    "leetcode": "leetcode" in request.credential_data,
                    "codeforces": "codeforces" in request.credential_data,
                    "linkedin": "linkedin" in request.credential_data,
                    "test": "test" in request.credential_data
                }
            }
        }
        
        # Calculate hash
        credential_json = json.dumps(credential_doc, sort_keys=True)
        hash_sha256 = hashlib.sha256(credential_json.encode()).hexdigest()
        
        # Create mock signature (in production, use proper cryptographic signing)
        signature_data = f"{credential_id}:{hash_sha256}"
        signature_b64 = base64.b64encode(signature_data.encode()).decode()
        
        # Create verification URL
        verification_url = f"https://verify.fairhiring.ai/credential/{credential_id}?hash={hash_sha256[:16]}"
        
        return PassportResponse(
            credential_id=credential_id,
            hash=hash_sha256,
            signature=signature_b64,
            verification_url=verification_url,
            issued_at=credential_doc["issued_at"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Passport issuance failed: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "passport_issuance"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
