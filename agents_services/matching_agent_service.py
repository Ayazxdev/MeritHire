"""
Matching Agent Wrapper Service
FastAPI service that wraps the matching agent as an HTTP endpoint.
Port: 8003
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import os
from contextlib import asynccontextmanager

# Add agents path to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents_files', 'Clean_Hiring_System'))
# Also add skill_verification_agent to path for utils imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents_files', 'Clean_Hiring_System', 'skill_verification_agent'))

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for matching service"""
    # Startup tasks if any
    yield

app = FastAPI(title="Matching Agent Service", lifespan=lifespan, version="1.0.0")

class MatchAgentRequest(BaseModel):
    credential: Optional[dict] = None
    resume_text: Optional[str] = None
    job_description: dict

class MatchAgentResponse(BaseModel):
    match_score: int
    breakdown: Optional[dict] = None

@app.post("/run", response_model=MatchAgentResponse)
async def run_matching(request: MatchAgentRequest):
    """
    Run matching agent using real-time dictionary matching.
    Can optionally fetch credential via ArmorIQ SDK if only resume_text is provided.
    """
    try:
        from matching_agent.agents.matching_agent import MatchingAgent
        try:
            from agents_services.armoriq_client import get_armoriq_client
        except ImportError:
            import sys
            import os
            sys.path.append(os.path.dirname(__file__))
            from armoriq_client import get_armoriq_client
        import json
        
        credential = request.credential

        # CONSUMER PATTERN: If no credential, fetch it via ArmorIQ SDK
        if not credential:
            if not request.resume_text:
                raise HTTPException(status_code=400, detail="Must provide 'credential' OR 'resume_text'")
            
            try:
                # 1. Initialize SDK
                client = get_armoriq_client()
                
                # 2. Capture Plan (Intent)
                # "I want to extract skills from this resume"
                # We use specific tool name 'skill_analysis' to ensure the plan maps correctly
                prompt = "Analyze skills from the provided resume text using skill_analysis tool."
                
                # Sync Domain with ArmorIQ Proxy
                mcp_url = os.getenv("MCP_TUNNEL_URL")
                if not mcp_url and os.path.exists("tunnel_url.txt"):
                    try:
                        with open("tunnel_url.txt", "r") as f:
                            mcp_url = f.read().strip() + "/mcp"
                    except: pass

                captured_plan = client.capture_plan(
                    llm="gpt-4",
                    prompt=prompt,
                    plan={
                        "goal": prompt,
                        "mcp_url": mcp_url or "http://localhost:8011/mcp",
                        "steps": [
                            {
                                "action": "skill_analysis",
                                "mcp": "hiring-mcp",
                                "params": {"resume_text": request.resume_text}
                            }
                        ]
                    }
                )
                
                # 3. Get Auth Token
                token_resp = client.get_intent_token(captured_plan)
                # FIX: object is not subscriptable and has no .get()
                token = getattr(token_resp, "token", None)
                if not token:
                    # Emergency fallback if it's actually a dict
                    try: token = token_resp["token"]
                    except: token = token_resp
                
                # 4. Invoke MCP Tool
                # MCP Name: 'hiring-mcp' (as defined in dashboard/walkthrough)
                # Tool Name: 'skill_analysis'
                mcp_result = client.invoke(
                    mcp="hiring-mcp",
                    action="skill_analysis",
                    intent_token=token,
                    params={
                        "application_id": 999, # Dummy ID for ad-hoc analysis
                        "resume_text": request.resume_text
                    }
                )
                
                if not mcp_result.get("success"):
                    raise RuntimeError(f"ArmorIQ Skill Analysis failed: {mcp_result.get('error')}")
                
                # 5. Extract Credential from MCP Result
                # Result format depends on MCP wrapper. Usually data -> output (from SkillAgentResponse)
                data = mcp_result.get("data", {})
                credential = data.get("output") or data # Fallback
                
            except Exception as sdk_err:
                print(f"SDK Integration Warning: {sdk_err}")
                # Fallback or re-raise depending on strictness. Here we re-raise because we can't match without data.
                raise HTTPException(status_code=502, detail=f"Failed to fetch skills via ArmorIQ: {str(sdk_err)}")

        agent = MatchingAgent()
        
        # Use internal _calculate_match for in-memory dictionaries
        match_analysis = agent._calculate_match(
            credential=credential,
            job=request.job_description
        )
        
        # Extract score and handle decision
        score = match_analysis.get("final_score", 0)
        
        return MatchAgentResponse(
            match_score=score,
            breakdown=match_analysis.get("breakdown", {})
        )
    
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.getLogger("uvicorn.error").error(f"Matching failed: {str(e)}")
        # Safe fallback
        return MatchAgentResponse(
            match_score=50,
            breakdown={"error": str(e)}
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "matching_agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
