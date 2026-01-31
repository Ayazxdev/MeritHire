"""
LinkedIn Parser Service
FastAPI service that parses LinkedIn profile PDFs.
Port: 8008
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import sys
import os
import logging
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents_files', 'Clean_Hiring_System'))
# Also add skill_verification_agent to path for utils imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents_files', 'Clean_Hiring_System', 'skill_verification_agent'))

app = FastAPI(title="LinkedIn Parser Service", version="1.0.0")
logger = logging.getLogger("uvicorn.error")

linkedin_parser = None


@app.on_event("startup")
async def startup():
    """Initialize LinkedIn parser on startup"""
    global linkedin_parser
    try:
        from skill_verification_agent.agents.linkedin_parser import LinkedInPDFParser
        linkedin_parser = LinkedInPDFParser()
        logger.info("LinkedIn parser initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize LinkedIn parser: {str(e)}")


class LinkedInRequest(BaseModel):
    pdf_path: Optional[str] = None  # Path to uploaded PDF
    linkedin_url: Optional[str] = None  # For future scraping


class LinkedInResponse(BaseModel):
    experience: list
    education: list
    skills: list
    certifications: Optional[list] = None
    summary: Optional[str] = None


@app.post("/parse", response_model=LinkedInResponse)
async def parse_linkedin(request: Optional[LinkedInRequest] = None, file: Optional[UploadFile] = File(None)):
    """
    Parse LinkedIn profile from uploaded PDF or file path
    """
    global linkedin_parser
    
    try:
        # Lazy initialization
        if linkedin_parser is None:
            from skill_verification_agent.agents.linkedin_parser import LinkedInPDFParser
            linkedin_parser = LinkedInPDFParser()
        
        tmp_path = None
        
        if file and file.filename:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name
        elif request and request.pdf_path:
            tmp_path = request.pdf_path
        elif request and request.linkedin_url:
            # Handle path in linkedin_url if that's where it's passed
            tmp_path = request.linkedin_url
        
        if not tmp_path or not os.path.exists(tmp_path):
             # Fallback: check if we have text directly
             # (LinkedInParser might not support text-only yet, but we'll return empty if so)
             return LinkedInResponse(experience=[], education=[], skills=[])

        try:
            # Parse LinkedIn PDF
            result = linkedin_parser.parse(tmp_path) # Changed from parse_pdf to parse
            
            return LinkedInResponse(
                experience=result.get("experience", {}).get("timeline", []), # Adjusted path
                education=result.get("education", []),
                skills=result.get("skills", {}).get("claimed", []), # Adjusted path
                certifications=result.get("certifications", []),
                summary=result.get("summary")
            )
        finally:
            # Clean up temp file ONLY if we created it
            if file and file.filename and tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        logger.error(f"LinkedIn parsing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"LinkedIn parsing failed: {str(e)}"
        )


@app.post("/parse-path", response_model=LinkedInResponse)
async def parse_linkedin_path(request: LinkedInRequest):
    """
    Parse LinkedIn profile from file path
    (Alternative endpoint if file is already on server)
    """
    global linkedin_parser
    
    try:
        if not request.pdf_path:
            raise HTTPException(status_code=400, detail="pdf_path required")
        
        if not os.path.exists(request.pdf_path):
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        # Lazy initialization
        if linkedin_parser is None:
            from skill_verification_agent.agents.linkedin_parser import LinkedInPDFParser
            linkedin_parser = LinkedInPDFParser()
        
        # Parse LinkedIn PDF
        result = linkedin_parser.parse(request.pdf_path) # Changed from parse_pdf to parse
        
        return LinkedInResponse(
            experience=result.get("experience", {}).get("timeline", []), # Adjusted path
            education=result.get("education", []),
            skills=result.get("skills", {}).get("claimed", []), # Adjusted path
            certifications=result.get("certifications", []),
            summary=result.get("summary")
        )
    
    except Exception as e:
        logger.error(f"LinkedIn parsing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"LinkedIn parsing failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "linkedin_parser",
        "parser_loaded": linkedin_parser is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)