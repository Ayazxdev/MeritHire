"""
Integration Example: Replace your current LLM setup with Dual LLM
This shows how to modify your existing ATS agent to use Ollama + OpenRouter
"""

import os
import sys
from dual_llm_setup_openrouter import DualLLMAgent


class ModernATSAgent:
    """
    Updated ATS agent using dual LLM approach
    """
    
    def __init__(self, openrouter_key: str = None):
        """
        Initialize with dual LLM support
        """
        # Initialize dual LLM agent
        self.llm = DualLLMAgent(openrouter_api_key=openrouter_key)
        
        print("✅ ATS Agent initialized with Dual LLM")
        print(f"   - Local: Ollama Llama 3.1 (FREE)")
        print(f"   - Cloud: OpenRouter ({self.llm.cloud_model})")
    
    
    def process_resume(self, resume_text: str, force_deep_check: bool = False) -> dict:
        """
        Process resume with hybrid LLM approach
        
        Args:
            resume_text: Extracted PDF text
            force_deep_check: Force cloud LLM check even if not suspicious
            
        Returns:
            Complete processing result
        """
        # Use dual LLM system
        result = self.llm.process_resume(resume_text, force_deep_check)
        
        # Format for your existing system
        formatted_result = {
            "ats_processing_result": {
                "source": "ats_resume_pdf",
                "extraction_method": "dual_llm_hybrid",
                "identity": {
                    "name": result["extraction"].get("name", "Unknown"),
                    "email": result["extraction"].get("email", None),
                },
                "experience": result["extraction"].get("experience", []),
                "projects": result["extraction"].get("projects", []),
                "skills": result["extraction"].get("skills", []),
            },
            "security_flags": [],
            "llm_metadata": {
                "models_used": result["models_used"],
                "processing_method": result["processing_method"],
                "total_cost": result["total_cost"],
                "flagged_for_review": result["flagged_for_review"]
            }
        }
        
        # Add security flags if deep check was performed
        if "security_check" in result:
            security = result["security_check"]
            
            formatted_result["security_flags"].append({
                "detection_type": security.get("injection_type", "none"),
                "severity": security.get("severity", "none"),
                "confidence": security.get("confidence", 0),
                "evidence": security.get("evidence", []),
                "patterns_found": security.get("patterns_found", []),
                "action": security.get("recommended_action", "proceed")
            })
        
        return formatted_result


# ============================================================================
# EXAMPLE: Replace your existing code
# ============================================================================

def example_old_vs_new():
    """
    Show the difference between old and new approach
    """
    
    print("="*70)
    print("OLD APPROACH (OpenAI GPT-4)")
    print("="*70)
    print("""
# Your old code (doesn't work without OpenAI key):

from langchain_openai import ChatOpenAI

class ATSAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            api_key=os.getenv("OPENAI_API_KEY")  # ❌ You don't have this
        )
    
    def extract(self, text):
        response = self.llm.invoke(f"Extract resume data: {text}")
        return response.content

# Problems:
# ❌ Requires OpenAI API key ($$$)
# ❌ No cost optimization
# ❌ Single model approach
# ❌ Expensive for bulk processing
    """)
    
    print("\n" + "="*70)
    print("NEW APPROACH (Ollama + OpenRouter)")
    print("="*70)
    print("""
# Your new code (works with OpenRouter):

from dual_llm_setup_openrouter import DualLLMAgent

class ATSAgent:
    def __init__(self):
        self.llm = DualLLMAgent()  # ✅ Uses Ollama + OpenRouter
    
    def extract(self, text):
        result = self.llm.process_resume(text)
        return result

# Benefits:
# ✅ FREE for 80% of resumes (Ollama)
# ✅ Paid only for suspicious cases (OpenRouter)
# ✅ Hybrid approach = best cost/quality
# ✅ 10-20x cheaper than OpenAI-only
    """)


def example_minimal_integration():
    """
    Minimal changes to your existing code
    """
    print("\n" + "="*70)
    print("MINIMAL INTEGRATION (Just 3 lines changed!)")
    print("="*70)
    
    print("""
# Step 1: Import the dual LLM agent
from dual_llm_setup_openrouter import DualLLMAgent

# Step 2: Replace your LLM initialization
# OLD:
# self.llm = ChatOpenAI(model="gpt-4")

# NEW:
self.llm = DualLLMAgent()

# Step 3: Use it the same way
result = self.llm.process_resume(resume_text)
extraction = result["extraction"]
    """)


def example_full_integration():
    """
    Show complete integration with your ATS system
    """
    print("\n" + "="*70)
    print("COMPLETE INTEGRATION EXAMPLE")
    print("="*70)
    
    # Initialize agent
    agent = ModernATSAgent()
    
    # Test resume
    test_resume = """
David Chen
david.chen@email.com | GitHub: github.com/dchen

Professional Experience

Senior ML Engineer                           Mar 2019 - Present
TechCorp AI Division
- Built production ML pipelines serving 10M+ users
- Reduced inference latency by 45% using TensorRT
- Led team of 4 engineers

Machine Learning Engineer                    Jun 2016 - Feb 2019
StartupXYZ
- Developed computer vision models (mAP: 92.3%)
- Deployed models to edge devices using ONNX

Skills: Python, TensorFlow, PyTorch, Docker, Kubernetes, AWS
    """
    
    print("\n--- Processing Resume ---")
    result = agent.process_resume(test_resume)
    
    # Display results
    import json
    print(json.dumps(result, indent=2))
    
    print(f"\n💰 Processing cost: ${result['llm_metadata']['total_cost']:.4f}")
    print(f"📊 Models used: {result['llm_metadata']['models_used']}")
    print(f"🚨 Flagged: {result['llm_metadata']['flagged_for_review']}")


if __name__ == "__main__":
    example_old_vs_new()
    example_minimal_integration()
    
    # Only run full test if Ollama is available
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            example_full_integration()
        else:
            print("\n⚠️  Start Ollama to see full integration example:")
            print("   ollama serve")
    except:
        print("\n⚠️  Start Ollama to see full integration example:")
        print("   ollama serve")
