"""
Bias Agent Wrapper Service
FastAPI service that wraps the bias detection agent as an HTTP endpoint.
Port: 8002
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

app = FastAPI(title="Bias Agent Service", version="1.0.0")

class BiasAgentRequest(BaseModel):
    credential: dict
    metadata: dict
    mode: str = "realtime"

class BiasAgentResponse(BaseModel):
    bias_detected: bool = False
    action: str = "proceed_to_matching"
    severity: str = "none"
    checks: Optional[dict] = None

@app.post("/run", response_model=BiasAgentResponse)
async def run_bias_detection(request: BiasAgentRequest):
    """
    Run bias detection agent
    """
    try:
        from bias_detection_agent.agents.bias_detection_agent import BiasDetectionAgent
        
        agent = BiasDetectionAgent()
        
        # Run real-time checks
        result = agent._run_realtime_checks(
            credential=request.credential,
            metadata=request.metadata
        )
        
        # Determine action and severity
        action = agent._determine_action(result)
        
        return BiasAgentResponse(
            bias_detected=result.get("bias_detected", False),
            action=action,
            severity=result.get("severity", "none"),
            checks=result
        )
    
    except Exception as e:
        import logging
        logging.getLogger("uvicorn.error").error(f"Bias detection failed: {str(e)}")
        # Safe fallback
        return BiasAgentResponse(
            bias_detected=False,
            action="proceed_to_matching",
            severity="none"
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "bias_agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
