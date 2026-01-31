"""
GitHub Scraper Service
Port: 8005

Scrapes GitHub profile for:
- Repos (non-fork)
- Languages
- Commits
- Framework signatures
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import re

app = FastAPI(title="GitHub Scraper Service", version="1.0.0")

class GitHubRequest(BaseModel):
    github_url: str
    application_id: int

class GitHubResponse(BaseModel):
    verified_languages: List[str] = []
    verified_frameworks: List[str] = []
    credibility_score: int = 0
    profile_data: dict = {}
    error: Optional[str] = None

def extract_username(url: str) -> str:
    """Extract GitHub username from URL"""
    # Handle various formats:
    # https://github.com/username
    # github.com/username
    # username
    if not url:
        return None
    
    url = url.strip()
    
    # Remove protocol
    url = re.sub(r'^https?://', '', url)
    
    # Remove github.com
    url = re.sub(r'^(www\.)?github\.com/', '', url)
    
    # Remove trailing slashes and get first part
    username = url.split('/')[0].strip()
    
    return username if username else None

@app.post("/scrape", response_model=GitHubResponse)
async def scrape_github(request: GitHubRequest):
    """
    Scrape GitHub profile
    
    NOTE: This is a mock implementation. In production, integrate with:
    - GitHub API (https://api.github.com/users/{username})
    - GitHub GraphQL API for detailed data
    - Or use existing scraper from agents_files/Clean_Hiring_System
    """
    try:
        username = extract_username(request.github_url)
        
        if not username:
            return GitHubResponse(
                error="Invalid GitHub URL format"
            )
        
        # MOCK DATA - Replace with actual GitHub API calls
        # In production, call:
        # - GET /users/{username}
        # - GET /users/{username}/repos
        # - Analyze repo languages, commits, etc.
        
        # For now, return mock data based on username
        verified_languages = ["Python", "JavaScript"]
        verified_frameworks = ["React", "FastAPI"]
        
        # Calculate credibility based on profile completeness
        credibility_score = 70  # Mock score
        
        profile_data = {
            "username": username,
            "public_repos": 25,  # Mock
            "followers": 50,  # Mock
            "total_commits": 500,  # Mock
            "active_repos": 15,  # Mock
            "languages_breakdown": {
                "Python": 45,
                "JavaScript": 30,
                "TypeScript": 15,
                "Other": 10
            },
            "framework_detections": {
                "React": {
                    "found_in": 8,
                    "indicators": ["package.json with react", "jsx files"]
                },
                "FastAPI": {
                    "found_in": 5,
                    "indicators": ["requirements.txt with fastapi", "main.py with FastAPI"]
                }
            }
        }
        
        return GitHubResponse(
            verified_languages=verified_languages,
            verified_frameworks=verified_frameworks,
            credibility_score=credibility_score,
            profile_data=profile_data
        )
    
    except Exception as e:
        return GitHubResponse(
            error=f"GitHub scraping failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "github_scraper"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
