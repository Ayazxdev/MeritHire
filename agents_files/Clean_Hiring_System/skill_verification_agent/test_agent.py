"""
Unit tests for Skill Verification Agent
"""
import unittest
from agents.skill_verification_agent import SkillVerificationAgent
from agents.data_normalizer import DataNormalizer
from utils.scoring import PortfolioScorer


class TestDataNormalizer(unittest.TestCase):
    def setUp(self):
        self.normalizer = DataNormalizer()
    
    def test_github_normalization(self):
        raw_github = {
            "data": {
                "total_commits_last_year": 200,
                "consistency_score": 75,
                "projects": [
                    {"project_score": 80},
                    {"project_score": 90}
                ],
                "top_languages": ["Python", "JavaScript"]
            }
        }
        
        result = self.normalizer.normalize_github(raw_github)
        
        self.assertEqual(result["commits_score"], 100)  # 200 commits = 100
        self.assertEqual(result["consistency_score"], 75)
        self.assertEqual(result["project_quality"], 85)  # (80+90)/2
    
    def test_leetcode_normalization(self):
        raw_leetcode = {
            "data": {
                "difficulty_breakdown": {
                    "easy": 10,
                    "medium": 5,
                    "hard": 2
                },
                "contest_rating": "Unrated",
                "max_rating": None,
                "top_language": "Python"
            }
        }
        
        result = self.normalizer.normalize_leetcode(raw_leetcode)
        
        # 10*1 + 5*3 + 2*5 = 35 points → (35/500)*100 = 7
        self.assertEqual(result["problem_solving_score"], 7)
    
    def test_codechef_normalization(self):
        raw_codechef = {
            "data": {
                "rating": 1500,
                "problems_solved": 100,
                "top_language": "C++"
            }
        }
        
        result = self.normalizer.normalize_codechef(raw_codechef)
        
        # 1500/2500 * 100 = 60
        self.assertEqual(result["competitive_rating"], 60)
        # 100/500 * 100 = 20
        self.assertEqual(result["problem_solving_score"], 20)


class TestPortfolioScorer(unittest.TestCase):
    def setUp(self):
        self.scorer = PortfolioScorer()
    
    def test_portfolio_scoring(self):
        normalized = {
            "github": {
                "commits_score": 80,
                "consistency_score": 75,
                "project_quality": 85
            },
            "leetcode": {
                "problem_solving_score": 50,
                "competitive_rating": 40
            }
        }
        
        result = self.scorer.calculate_portfolio_score(normalized)
        
        # GitHub: (80*0.3 + 75*0.3 + 85*0.4) * 0.6 = 48.6
        # LeetCode: (50*0.7 + 40*0.3) * 0.4 = 18.8
        # Total: ~67
        self.assertGreater(result["portfolio_score"], 60)
        self.assertLess(result["portfolio_score"], 70)
    
    def test_ats_manipulation_detection(self):
        # Normal resume
        normal_resume = "Experienced Python developer with 5 years of experience in web development."
        result1 = self.scorer.detect_ats_manipulation(normal_resume)
        self.assertFalse(result1["manipulated"])
        
        # Manipulated resume
        stuffed_resume = "Python Python React Node AWS Docker Python JavaScript Python React AWS Docker " * 10
        result2 = self.scorer.detect_ats_manipulation(stuffed_resume)
        self.assertTrue(result2["manipulated"])


class TestSkillVerificationAgent(unittest.TestCase):
    def setUp(self):
        self.agent = SkillVerificationAgent()
    
    def test_anonymization(self):
        application = {
            "name": "John Doe",
            "email": "john@example.com",
            "resume": "test resume",
            "github_url": "https://github.com/john",
            "gender": "M",
            "college": "MIT"
        }
        
        result = self.agent.anonymize_candidate(application)
        
        self.assertTrue(result["candidate_id"].startswith("anon_"))
        self.assertEqual(result["metadata"]["gender"], "M")
        self.assertEqual(result["resume"], "test resume")
    
    def test_portfolio_analysis(self):
        github_data = {
            "data": {
                "total_commits_last_year": 150,
                "consistency_score": 70,
                "projects": [{"project_score": 80}],
                "top_languages": ["Python"]
            }
        }
        
        result = self.agent.analyze_portfolio(github_data=github_data)
        
        self.assertIn("portfolio_score", result)
        self.assertIn("signal_strength", result)
        self.assertIn("github", result["evidence_sources"])


if __name__ == "__main__":
    unittest.main()
