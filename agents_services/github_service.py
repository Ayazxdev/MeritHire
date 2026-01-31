"""
GitHub Scraper Service
FastAPI service that scrapes GitHub profiles.
Port: 8005
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents_files', 'Clean_Hiring_System'))
# Also add skill_verification_agent to path for utils imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents_files', 'Clean_Hiring_System', 'skill_verification_agent'))

# Set GitHub PAT for API authentication (5000 req/hour instead of 60)
os.environ.setdefault("GITHUB_PAT", os.getenv("GITHUB_PAT", ""))

app = FastAPI(title="GitHub Scraper Service", version="1.0.0")
logger = logging.getLogger("uvicorn.error")

github_scraper = None


@app.on_event("startup")
async def startup():
    """Initialize GitHub scraper on startup"""
    global github_scraper
    try:
        from skill_verification_agent.scraper.github_api import GitHubAPIClient
        github_scraper = GitHubAPIClient()
        logger.info("GitHub scraper initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize GitHub scraper: {str(e)}")


class GitHubRequest(BaseModel):
    username: str
    github_url: Optional[str] = None  # Alternative: full URL


class GitHubResponse(BaseModel):
    username: str
    repos: list
    languages: dict
    commits: dict
    frameworks: list
    top_projects: list
    activity_score: int


@app.post("/scrape", response_model=GitHubResponse)
async def scrape_github(request: GitHubRequest):
    """
    Scrape GitHub profile for skills and activity
    """
    global github_scraper
    
    try:
        # Extract username from URL if provided
        username = request.username
        if request.github_url and not username:
            username = request.github_url.rstrip('/').split('/')[-1]
        
        if not username:
            raise HTTPException(status_code=400, detail="Username or github_url required")
        
        # Lazy initialization
        if github_scraper is None:
            from skill_verification_agent.scraper.github_api import GitHubAPIClient
            github_scraper = GitHubAPIClient()
        
        # Scrape GitHub with error handling
        try:
            result = github_scraper.analyze_full_profile(username)
        except Exception as scrape_error:
            logger.error(f"GitHub API scraping failed for {username}: {str(scrape_error)}")
            # Return empty/minimal response instead of failing
            return GitHubResponse(
                username=username,
                repos=[],
                languages={},
                commits={},
                frameworks=[],
                top_projects=[],
                activity_score=0
            )
        
        # Map to response model with safe defaults
        skill_signal = result.get("skill_signal", {})
        consistency = result.get("consistency_signal", {})
        
        return GitHubResponse(
            username=username,
            repos=skill_signal.get("best_repositories", []),
            languages=skill_signal.get("languages_by_bytes", {}),
            commits=consistency,
            frameworks=skill_signal.get("verified_languages", []),
            top_projects=skill_signal.get("best_repositories", [])[:3],
            activity_score=result.get("credibility_signal", {}).get("credibility_score", 0)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GitHub scraping failed for {request.username}: {str(e)}")
        # Return minimal response instead of 500 error
        return GitHubResponse(
            username=request.username,
            repos=[],
            languages={},
            commits={},
            frameworks=[],
            top_projects=[],
            activity_score=0
        )



@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "github_scraper",
        "scraper_loaded": github_scraper is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)