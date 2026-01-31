
import sys
import os

# Add agents path
sys.path.insert(0, os.path.join(os.getcwd(), 'agents_files', 'Clean_Hiring_System'))
sys.path.insert(0, os.path.join(os.getcwd(), 'agents_files', 'Clean_Hiring_System', 'skill_verification_agent'))

try:
    from skill_verification_agent.agents.ats import ATSEvidenceAgent
    print("Successfully imported ATSEvidenceAgent")
    agent = ATSEvidenceAgent()
    print("Successfully initialized ATSEvidenceAgent")
    
    pdf_path = r"D:\Hiring\backend\uploads\ANON-1FCEA2335592\26\Udbhaw_Resume (1).pdf"
    if os.path.exists(pdf_path):
        print(f"File exists: {pdf_path}")
    else:
        print(f"File NOT found: {pdf_path}")
        
except Exception as e:
    print(f"Failed: {e}")
    import traceback
    traceback.print_exc()
