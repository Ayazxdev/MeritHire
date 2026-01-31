import os
import json
import logging
import sys
from unittest.mock import MagicMock, patch

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Add module path
sys.path.append(os.path.join(os.getcwd(), "skill_verification_agent"))

from agents.ats import ATSEvidenceAgent

def analyze_resume(pdf_path, output_file):
    print(f"🔍 Analyzing: {pdf_path}")
    
    # Mock dependencies to run isolated detection test
    mock_db = MagicMock()
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = '{}' # Empty valid JSON for extraction phase if it gets there

    # Patch Dual-LLM to avoid API key errors (unless we want to test it specifically)
    # We'll allow it to instantiate if possible, but fallback to mock if it crashes
    with patch('utils.manipulation_detector.PromptInjectionDefender') as MockDefender:
        # We mock the defender so we don't need OpenAI keys
        # We set it to return "Safe" so we can see if OTHER detectors (Regex, Semantic, WhiteText) catch it.
        # If the user wants Dual-LLM to catch it, we'd need real LLM or simulated response.
        # Given "David Chen" attack text is subtle ("semantic"), Dual-LLM *might* catch it if real,
        # but the Semantic Evasion Detector is definitely designed for it.
        mock_defender_instance = MockDefender.return_value
        mock_defender_instance.inspect_for_injection.return_value = {"safe": True, "reason": "Mocked safe"}

        # Initialize Agent
        agent = ATSEvidenceAgent(llm=mock_llm, db_session=mock_db)
        
        # Ensure ReviewService mock is ready
        agent.review_service = MagicMock()
        agent.review_service.is_blacklisted.return_value = False # Force clean slate for analysis
        agent.review_service.queue_for_review = MagicMock()

        try:
            # Run the Full Pipeline
            result = agent.extract_evidence(
                pdf_path=pdf_path,
                evaluation_id="MANUAL_TEST_DAVID_CHEN",
                candidate_email="david.chen@example.com"
            )
            
            # Check if anything was queued for review (flagged) variables
            queued_items = []
            if agent.review_service.queue_for_review.called:
                for call in agent.review_service.queue_for_review.call_args_list:
                    # call.kwargs contains the details
                    queued_items.append(call.kwargs)
            
            # Construct Final Report
            # Extract security evidence from the first queued item (if any)
            security_detection = {}
            if queued_items:
                # Get the evidence from the first security flag
                security_detection = queued_items[0].get("evidence", {})
            
            final_report = {
                "ats_processing_result": result,
                "security_detection": security_detection,
                "detection_summary": {
                    "flags_count": len(queued_items),
                    "flag_types": [q.get("detection_type") for q in queued_items]
                }
            }
            
            # Save Report
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(final_report, f, indent=2)
                
            print(f"✅ Analysis Complete.")
            print(f"📂 Output saved to: {output_file}")
            print("\n--- DETECTION HIGHLIGHTS ---")
            
            if queued_items:
                print(f"🚩 SECURITY ALERTS CONFIGURED: {len(queued_items)}")
                for item in queued_items:
                    print(f"   [!] Type: {item.get('detection_type')}")
                    print(f"       Severity: {item.get('severity')}")
                    print(f"       Evidence: {item.get('evidence', {}).get('type') or 'See JSON'}")
            else:
                print("✅ No security flags raised.")

            if result.get("status"):
                print(f"Status: {result.get('status')}")
                print(f"Reason: {result.get('reason')}")

        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    target_pdf = r"test_attacks\David Chen - Senior ML Engineer.pdf"
    output_json = r"test_attacks\david_chen_analysis.json"
    
    if not os.path.exists(target_pdf):
        print(f"❌ File not found: {target_pdf}")
    else:
        analyze_resume(target_pdf, output_json)
