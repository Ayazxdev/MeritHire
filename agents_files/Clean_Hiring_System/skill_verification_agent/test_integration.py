import os
import io
import unittest
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.review_models import Base, HumanReviewQueue, CandidateBlacklist
from agents.ats import ATSEvidenceAgent
from utils.pdf_layer_extractor import WhiteTextDetector

# Setup in-memory DB for testing
engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

class TestATSIntegration(unittest.TestCase):
    
    def setUp(self):
        self.db = SessionLocal()
        # Mock LLM since we only test security logic
        self.mock_llm = MagicMock()
        self.agent = ATSEvidenceAgent(self.mock_llm, self.db)
        
        # Mock white text detector to control outcome
        self.agent.white_text_detector = MagicMock()
        self.agent.white_text_detector.detect_white_text.return_value = {
            "white_text_detected": False, "action": "proceed", "severity": "low"
        }
        
    def tearDown(self):
        self.db.close()
        
    def test_clean_resume_flow(self):
        """Test clean resume proceeds to processing"""
        self.agent._stage0_canonicalize = MagicMock(return_value="Clean text")
        self.agent.injection_scanner.scan = MagicMock(return_value={
            "injection_detected": False, "action": "proceed"
        })
        
        # Bypass file opening
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(read_data=b"PDF data")):
            with unittest.mock.patch('os.path.exists', return_value=True):
                 self.agent.extract_evidence("dummy.pdf", evaluation_id="123", candidate_email="clean@test.com")
        
        # Verify NO review queue entry
        queue = self.db.query(HumanReviewQueue).all()
        self.assertEqual(len(queue), 0)

    def test_white_text_queueing(self):
        """Test white text triggers review queue"""
        # Simulate white text detection
        self.agent.white_text_detector.detect_white_text.return_value = {
            "white_text_detected": True, 
            "action": "queue_for_review", 
            "severity": "high",
            "suspicious_matches": ["ignore"],
            "hidden_word_count": 60
        }
        
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(read_data=b"PDF data")):
            with unittest.mock.patch('os.path.exists', return_value=True):
                 result = self.agent.extract_evidence("dummy.pdf", evaluation_id="eval_wt", candidate_email="hacker@test.com")
        
        # Verify Status
        self.assertEqual(result["status"], "PENDING_HUMAN_REVIEW")
        
        # Verify DB entry
        queue = self.db.query(HumanReviewQueue).filter_by(evaluation_id="eval_wt").first()
        self.assertIsNotNone(queue)
        self.assertEqual(queue.detection_type, "white_text")
        self.assertEqual(queue.severity, "high")

    def test_blacklist_blocking(self):
        """Test blacklisted candidate is blocked immediately"""
        # Manually blacklist a user
        import hashlib
        email = "banned@test.com"
        email_hash = hashlib.sha256(email.encode()).hexdigest()
        
        blacklist = CandidateBlacklist(
            candidate_hash=email_hash,
            reason="cheating",
            detection_type="prompt_injection",
            evidence_snapshot={}
        )
        self.db.add(blacklist)
        self.db.commit()
        
        # Try to process
        with unittest.mock.patch('os.path.exists', return_value=True):
             result = self.agent.extract_evidence("dummy.pdf", evaluation_id="eval_banned", candidate_email=email)
             
        self.assertEqual(result["status"], "BLACKLISTED_PREVIOUSLY")

if __name__ == '__main__':
    unittest.main()
