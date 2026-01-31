import os
import json
import logging
import sys
# Add skill_verification_agent to python path
sys.path.append(os.path.join(os.getcwd(), "skill_verification_agent"))

from unittest.mock import MagicMock
from agents.ats import ATSEvidenceAgent
from services.review_service import ReviewService

# Create logs directory if it doesn't exist to prevent logger errors
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(level=logging.INFO)

def test_detection_system():
    """
    Test all attack scenarios against the ATS Agent
    """
    
    # Initialize agent with Mock DB/LLM
    # We mock DB session to prevent actual DB writes but allow logic flow
    mock_db = MagicMock()
    mock_llm = MagicMock()
    
    # Configure mock LLM to return safe JSON for "clean" parts of flow
    mock_llm.invoke.return_value = '{"start_date": "2023-01", "end_date": "2023-12"}'
    
    # Patch PromptInjectionDefender (Dual-LLM) to avoid OpenAI init
    from unittest.mock import patch
    # Note: We must patch where it is defined since ats imports it locally
    with patch('utils.manipulation_detector.PromptInjectionDefender') as MockDefender:
        # Check if we need to mock the instance
        mock_defender_instance = MockDefender.return_value
        mock_defender_instance.inspect_for_injection.return_value = {"safe": True}
        
        # We need to ensure detectors are initialized. 
        # ATSEvidenceAgent initializes them in __init__
        agent = ATSEvidenceAgent(llm=mock_llm, db_session=mock_db)
        
        # Ensure ReviewService is present (mocked internally by agent init or we force it)
        agent.review_service = MagicMock()
        agent.review_service.is_blacklisted.return_value = False
        
        # Override the mocked defender's behavior for specific tests?
        # We can do that inside the loop or set it on `agent.dual_llm_defender` (which is the mock instance)
        
        # For tests that expect dual-llm detection, we can override later.
        
        test_cases = [
            {
                "name": "Clean Resume",
                "file": "test_attacks/resume_clean.pdf",
                "expected_status": ["proceed", "success", "processed", "safe"], # Flexible matching
                "dual_llm_result": {"safe": True}
            },
            {
                "name": "White Text Attack",
                "file": "test_attacks/resume_white_text.pdf",
                "expected_status": ["PENDING_HUMAN_REVIEW", "BLACKLISTED", "queue_for_review"],
                "notes": "White text should trigger review queue",
                 "dual_llm_result": {"safe": True}
            },
            {
                "name": "Prompt Injection #1",
                "file": "test_attacks/resume_prompt_injection_1.pdf",
                "expected_status": ["BLACKLISTED", "immediate_blacklist"],
                 "notes": "Direct injection should blacklist",
                 "dual_llm_result": {"safe": True} # Caught by Regex
            },
            {
                "name": "Prompt Injection #2",
                "file": "test_attacks/resume_prompt_injection_2.pdf",
                 "expected_status": ["BLACKLISTED", "immediate_blacklist"],
                 "dual_llm_result": {"safe": True} # Caught by Regex
            },
             {
                "name": "Combined Attack",
                "file": "test_attacks/resume_combined_attack.pdf",
                "expected_status": ["BLACKLISTED", "immediate_blacklist"],
                "dual_llm_result": {"safe": True}
            }
        ]
        
        results = []
        
        print("\n" + "="*60)
        print("🚀 RUNNING DETECTION TEST SUITE")
        print("="*60)
        
        for test in test_cases:
            print(f"\n🔹 Testing: {test['name']}")
            
            if not os.path.exists(test['file']):
                print(f"❌ File not found: {test['file']}")
                continue
            
            # Configure Dual LLM Mock behavior for this test
            if "dual_llm_result" in test:
                 agent.dual_llm_defender.inspect_for_injection.return_value = test["dual_llm_result"]
            
            # Process resume
            try:
                result = agent.extract_evidence(
                    pdf_path=test['file'],
                    evaluation_id=f"test_{test['name'].replace(' ', '_')}",
                    candidate_email="test@example.com"
                )
            except Exception as e:
                print(f"❌ Exception: {e}")
                result = {"status": "ERROR"}
            
            # Check result
            status = result.get("status", "processed")
            # Also check if it was queued (mock review service)
            queued = agent.review_service.queue_for_review.called
            
            # Determine if pass
            # Success if status is in expected list OR if expected is BLACKLISTED and we queued/blocked
            passed = status in test['expected_status']
            
            # Reset mock for next test
            agent.review_service.queue_for_review.reset_mock()
            
            print(f"   Status: {status}")
            if passed:
                print(f"   ✅ PASS")
            else:
                print(f"   ❌ FAIL: Expected one of {test['expected_status']}, got {status}")
            
            results.append({
                "test": test['name'],
                "passed": passed,
                "actual": status
            })
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed_count = sum(1 for r in results if r['passed'])
    print(f"Total Passed: {passed_count}/{len(results)}")
    
    for r in results:
        icon = "✅" if r['passed'] else "❌"
        print(f"{icon} {r['test']}: {r['actual']}")

if __name__ == "__main__":
    test_detection_system()
