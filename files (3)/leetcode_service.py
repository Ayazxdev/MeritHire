"""
LeetCode Scraper Service
Port: 8006

Scrapes LeetCode profile for:
- Problems solved
- Contest rating
- Skill tags
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import re

app = FastAPI(title="LeetCode Scraper Service", version="1.0.0")

class LeetCodeRequest(BaseModel):
    leetcode_url: str
    application_id: int

class LeetCodeResponse(BaseModel):
    problems_solved: int = 0
    contest_rating: Optional[int] = None
    skill_signal: str = "NONE"  # "NONE" | "DSA" | "COMPETITIVE"
    profile_data: dict = {}
    error: Optional[str] = None

def extract_username(url: str) -> str:
    """Extract LeetCode username from URL"""
    if not url:
        return None
    
    url = url.strip()
    
    # Remove protocol
    url = re.sub(r'^https?://', '', url)
    
    # Remove leetcode.com
    url = re.sub(r'^(www\.)?leetcode\.com/', '', url)
    
    # Remove trailing slashes and get first part (usually after /u/ or direct)
    parts = url.split('/')
    
    # Handle /u/username format
    if 'u' in parts:
        idx = parts.index('u')
        if idx + 1 < len(parts):
            return parts[idx + 1]
    
    # Otherwise return first non-empty part
    for part in parts:
        if part:
            return part
    
    return None

@app.post("/scrape", response_model=LeetCodeResponse)
async def scrape_leetcode(request: LeetCodeRequest):
    """
    Scrape LeetCode profile
    
    NOTE: This is a mock implementation. In production, integrate with:
    - LeetCode GraphQL API
    - Or use existing scraper from agents_files/Clean_Hiring_System
    """
    try:
        username = extract_username(request.leetcode_url)
        
        if not username:
            return LeetCodeResponse(
                error="Invalid LeetCode URL format"
            )
        
        # MOCK DATA - Replace with actual LeetCode API calls
        # In production, call LeetCode GraphQL:
        # query {
        #   matchedUser(username: "username") {
        #     submitStats { acSubmissionNum { difficulty, count } }
        #     profile { ranking, reputation }
        #   }
        # }
        
        # For now, return mock data
        problems_solved = 227  # Mock
        contest_rating = 1650  # Mock
        
        # Determine skill signal
        if problems_solved > 200:
            skill_signal = "DSA"
        elif contest_rating and contest_rating > 1800:
            skill_signal = "COMPETITIVE"
        elif problems_solved > 50:
            skill_signal = "DSA"
        else:
            skill_signal = "NONE"
        
        profile_data = {
            "username": username,
            "total_solved": problems_solved,
            "easy_solved": 100,  # Mock
            "medium_solved": 100,  # Mock
            "hard_solved": 27,  # Mock
            "contest_rating": contest_rating,
            "global_ranking": 25000,  # Mock
            "acceptance_rate": 65.5,  # Mock
            "problem_categories": {
                "Array": 45,
                "Dynamic Programming": 30,
                "Trees": 25,
                "Graphs": 20,
                "Other": 107
            }
        }
        
        return LeetCodeResponse(
            problems_solved=problems_solved,
            contest_rating=contest_rating,
            skill_signal=skill_signal,
            profile_data=profile_data
        )
    
    except Exception as e:
        return LeetCodeResponse(
            error=f"LeetCode scraping failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "leetcode_scraper"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
