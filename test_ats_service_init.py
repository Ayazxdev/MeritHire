
import sys
import os
import logging

# Simulation of ats_service.py setup
path = os.path.join(os.getcwd(), 'agents_files', 'Clean_Hiring_System')
sys.path.insert(0, path)
sys.path.insert(0, os.path.join(path, 'skill_verification_agent'))

logging.basicConfig(level=logging.INFO)

try:
    from skill_verification_agent.agents.ats import ATSEvidenceAgent
    print("Successfully imported ATSEvidenceAgent")
    ats_agent = ATSEvidenceAgent(llm=None)
    print("ATS Agent initialized successfully")
except Exception as e:
    print(f"Failed to initialize ATS agent: {e}")
    import traceback
    traceback.print_exc()
