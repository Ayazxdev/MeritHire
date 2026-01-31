
import json
import random
import os
from pathlib import Path

def generate_mock_data():
    """
    Generates synthetic candidate data with controlled bias patterns for testing.
    """
    candidates = []
    
    # Colleges
    tier1_colleges = ["IIT Delhi", "IIT Bombay", "BITS Pilani", "IIIT Hyderabad", "NIT Trichy"]
    tier2_colleges = ["VIT", "Manipal", "SRM", "Anna University", "Mumbai University"]
    
    # Skills template
    all_skills = ["Python", "JavaScript", "React", "Machine Learning", "Data Structures", "Node.js", "Java", "C++"]

    # Generate 100 candidates
    for i in range(100):
        # 1. Gender Bias Setup (Females have slightly lower confidence scores on average)
        gender = random.choice(["M", "F"])
        
        # 2. College Bias Setup (Tier 1 gets better scores)
        if random.random() < 0.3:
            college = random.choice(tier1_colleges)
            college_tier = 1
        else:
            college = random.choice(tier2_colleges)
            college_tier = 2
            
        # 3. GitHub Age
        account_age = round(random.uniform(0.5, 6.0), 1)
        
        # Base confidence
        if gender == "M":
            base_score = random.randint(65, 90)
        else:
            base_score = random.randint(55, 80) # Bias injection!
            
        # College boost
        if college_tier == 1:
            base_score += 5
            
        # Ensure bounds
        base_score = min(95, max(40, base_score))
        
        # Skill count
        num_skills = random.randint(3, 8)
        verified_skills = random.sample(all_skills, num_skills)
        
        # Employment Gap
        gaps = 0
        if random.random() < 0.15:
            gaps = random.randint(1, 12) # months
            
        candidate = {
            "candidate_id": f"anon_{1000+i}",
            "verified_skills": verified_skills,
            "skill_confidence": base_score,
            "credential_status": "VERIFIED" if base_score > 70 else "PROVISIONAL",
            "metadata": {
                "gender": gender,
                "college": college,
                "age": random.randint(21, 35),
                "location": "India",
                "employment_gaps": gaps
            },
            "evidence": {
                "portfolio_score": base_score - random.randint(-5, 5),
                "test_score": None
            },
            "evidence_details": {
                "github": {
                    "account_age_years": account_age,
                    "commits_analyzed": random.randint(50, 500),
                    "project_quality": random.randint(40, 90)
                },
                "leetcode": {
                    "problems_solved": random.randint(0, 300),
                    "contest_rating": random.randint(1200, 2000)
                }
            },
            "timestamp": "2026-01-20T10:00:00Z"
        }
        candidates.append(candidate)
        
    # Ensure output directory exists
    os.makedirs("data", exist_ok=True)
    
    output_path = Path("data/mock_history_db.json")
    with open(output_path, "w") as f:
        json.dump(candidates, f, indent=2)
        
    print(f"✅ Generated {len(candidates)} mock candidates at {output_path}")

if __name__ == "__main__":
    generate_mock_data()
