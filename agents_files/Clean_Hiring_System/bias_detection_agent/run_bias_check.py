import json
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
# Also add current dir
sys.path.insert(0, str(Path(__file__).parent))

from agents.bias_detection_agent import BiasDetectionAgent

def main():
    print("="*60)
    print("⚖️  BIAS DETECTION AGENT (Standalone Test)")
    print("="*60)
    
    # Initialize Agent
    agent = BiasDetectionAgent()
    
    # Run Analysis on the mock credential we just created
    json_path = str(Path(__file__).parent.parent / "final_credential.json")
    
    if not os.path.exists(json_path):
        print(f"❌ Error: {json_path} not found")
        return

    print(f"📂 Analyzing: {json_path}")
    print("⏳ Running Batch Analysis (with Mock History)...")
    
    try:
        report = agent.run_analysis(json_path, mode="batch")
        
        print(f"\n📊 REPORT SUMMARY:")
        print(f"   Bias Detected: {report['bias_detected']}")
        print(f"   Severity:      {report['severity'].upper()}")
        print(f"   Action:        {report['action']}")
        
        if report["bias_detected"]:
            print(f"\n🚩 DETAILS:")
            print(json.dumps(report["details"], indent=2))
            
        # Save Report
        with open("bias_report.json", "w") as f:
            json.dump(report, f, indent=2)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
