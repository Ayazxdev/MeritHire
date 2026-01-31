import sys
import os
import json

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents_files', 'Clean_Hiring_System'))

from skill_verification_agent.agents.ats import ATSEvidenceAgent

def test_ats():
    try:
        agent = ATSEvidenceAgent(llm=None)
        # Assuming there's a sample resume or we use a dummy path
        # Let's find a real resume in the project if possible
        resume_path = r"D:\Hiring\agents_files\Clean_Hiring_System\tests\test_attacks\David Chen - Senior ML Engineer.pdf"
        if not os.path.exists(resume_path):
             # Create a dummy text if no pdf
             print("Sample resume not found, testing with dummy text")
             # We might need to mock extract_text if it's used
             pass
        
        print("\n--- TRIGGERING ATS DEEP ANALYSIS ---")
        result = agent.extract_evidence(resume_path, deep_check=True)
        print("\n--- ATS OUTPUT ---")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ats()
