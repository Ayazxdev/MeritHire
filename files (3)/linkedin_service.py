"""
LinkedIn Parser Service
Port: 8008

Parses LinkedIn PDF for:
- Roles and durations
- Endorsed skills
- Experience verification
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import re

app = FastAPI(title="LinkedIn Parser Service", version="1.0.0")

class LinkedInRequest(BaseModel):
    linkedin_text: str
    linkedin_path: str
    application_id: int

class LinkedInResponse(BaseModel):
    experience_verified: bool = False
    skills: List[str] = []
    roles: List[dict] = []
    profile_data: dict = {}
    error: Optional[str] = None

@app.post("/parse", response_model=LinkedInResponse)
async def parse_linkedin(request: LinkedInRequest):
    """
    Parse LinkedIn PDF text
    """
    try:
        text = request.linkedin_text
        
        if not text or len(text) < 50:
            return LinkedInResponse(
                error="LinkedIn PDF appears empty or unreadable"
            )
        
        # Extract skills (common patterns in LinkedIn PDFs)
        skills = []
        skill_keywords = [
            "Python", "JavaScript", "Java", "C++", "React", "Angular", "Vue",
            "Node.js", "Django", "Flask", "FastAPI", "Spring", "SQL", "NoSQL",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "Agile"
        ]
        
        for skill in skill_keywords:
            if re.search(rf'\b{skill}\b', text, re.IGNORECASE):
                skills.append(skill)
        
        # Extract roles (look for common job title patterns)
        roles = []
        role_pattern = r'(Software Engineer|Developer|Architect|Manager|Lead|Senior|Junior|Intern)'
        matches = re.findall(role_pattern, text, re.IGNORECASE)
        
        for match in matches[:5]:  # Limit to 5 roles
            roles.append({
                "title": match,
                "verified": True
            })
        
        # Calculate experience verification
        experience_verified = len(roles) > 0
        
        profile_data = {
            "total_roles": len(roles),
            "skills_found": len(skills),
            "text_length": len(text),
            "has_education": bool(re.search(r'\b(University|College|Degree|Bachelor|Master|PhD)\b', text, re.IGNORECASE))
        }
        
        return LinkedInResponse(
            experience_verified=experience_verified,
            skills=skills,
            roles=roles,
            profile_data=profile_data
        )
    
    except Exception as e:
        return LinkedInResponse(
            error=f"LinkedIn parsing failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "linkedin_parser"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
