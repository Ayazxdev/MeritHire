"""
Skill Agent Wrapper Service
FastAPI service that wraps the skill verification agent as an HTTP endpoint.
Port: 8001
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Add agents path to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents_files', 'Clean_Hiring_System'))
# Also add skill_verification_agent to path for utils imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents_files', 'Clean_Hiring_System', 'skill_verification_agent'))

app = FastAPI(title="Skill Agent Service", version="1.0.0")

class SkillAgentRequest(BaseModel):
    application_id: int
    resume_text: str
    github_url: Optional[str] = None
    leetcode_url: Optional[str] = None
    codeforces_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    anon_id: str
    evidence: Optional[dict] = {}


class SkillAgentResponse(BaseModel):
    output: dict
    explanation: Optional[str] = None
    flags: list = []


@app.post("/run", response_model=SkillAgentResponse)
async def run_skill_verification(request: SkillAgentRequest):
    """
    Run skill verification agent using 2026 Evidence Graph architecture.
    """
    try:
        from skill_verification_agent.agents.evidence_graph_builder import EvidenceGraphBuilder
        from skill_verification_agent.agents.skill_verification_agent_v2 import SkillVerificationAgentV2
        
        # 1. Build Evidence Graph
        builder = EvidenceGraphBuilder()
        evidence = request.evidence or {}
        
        # Evidence graph builder likes named outputs
        graph = builder.build_evidence_graph(
            ats_output=evidence.get("ats"),
            linkedin_output=evidence.get("linkedin"),
            github_output=evidence.get("github"),
            leetcode_output=evidence.get("leetcode"),
            codechef_output=evidence.get("codeforces"), # Maps to CP skill in builder
            evaluation_id=str(request.application_id)
        )
        
        # 2. Issue Credential
        import asyncio
        agent = SkillVerificationAgentV2()
        credential = await asyncio.to_thread(agent.issue_credential, graph)
        
        return SkillAgentResponse(
            output=credential,
            explanation=f"Skill verification complete for application {request.application_id}. Level: {credential.get('experience_level', 'Unknown')}",
            flags=credential.get("flags", [])
        )
    
    except Exception as e:
        import logging
        logging.getLogger("uvicorn.error").error(f"Skill verification failed: {str(e)}")
        # Fallback to mock if integration fails (to keep pipeline running during dev)
        return SkillAgentResponse(
            output={
                "skills": ["General Programming"],
                "confidence": 0.5,
                "test_required": True,
                "error": str(e)
            },
            explanation="Failed to run SkillVerificationAgentV2. Using fallback response.",
            flags=["INTEGRATION_ERROR"]
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "skill_agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
