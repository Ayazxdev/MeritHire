
import sys
import os
import json
import logging

# Add path
sys.path.insert(0, os.path.join(os.getcwd(), 'agents_files', 'Clean_Hiring_System'))

try:
    from utils.dual_llm_client import DualLLMClient
    
    print("Initializing DualLLMClient (Regex Backend)...")
    client = DualLLMClient()
    
    sample_text = """
    EXPERIENCE SECTION:
    Senior Software Engineer
    Tech Corp Inc.
    Jan 2020 - Present
    - Led the migration of monolith to microservices using Python, FastAPI, and Kubernetes.
    - Improved system performance by 30% using Redis caching.
    
    Projects:
    - Portfolio Website | Built with React and Node.js
    <<<END>>>
    """
    
    print("Testing extraction...")
    result = client.call_ollama(sample_text)
    
    print(f"Success: {result['success']}")
    print(f"Model: {result['model']}")
    content = json.loads(result['content'])
    print(f"Extracted Skills: {[s['skill'] for s in content.get('skills', [])]}")
    print(f"Extracted Experience: {[e['role'] for e in content.get('experience', [])]}")
    
except Exception as e:
    print(f"Test Failed: {e}")
    import traceback
    traceback.print_exc()
