"""
Example usage of Bias Detection Meta-Agent
"""
import json
from agents.bias_detection_agent import BiasDetectionAgent

# Initialize agent
agent = BiasDetectionAgent()

# Sample candidate data (simulating output from skill verification)
# This would normally come from the matching pipeline
candidates = [
    # Male candidates
    {"candidate_id": "anon_001", "score": 85, "metadata": {"gender": "M", "college": "IIT Delhi", "college_tier": 1, "location": "Delhi"}, "evidence": {"portfolio_score": 85, "test_score": None, "interview_signal": 80}},
    {"candidate_id": "anon_002", "score": 78, "metadata": {"gender": "M", "college": "MIT", "college_tier": 1, "location": "Boston"}, "evidence": {"portfolio_score": 78, "test_score": 80, "interview_signal": 85}},
    {"candidate_id": "anon_003", "score": 72, "metadata": {"gender": "M", "college": "Local College", "college_tier": 3, "location": "Mumbai"}, "evidence": {"portfolio_score": 72, "test_score": 70, "interview_signal": 75}},
    {"candidate_id": "anon_004", "score": 88, "metadata": {"gender": "M", "college": "NIT", "college_tier": 1, "location": "Chennai"}, "evidence": {"portfolio_score": 88, "test_score": None, "interview_signal": 82}},
    {"candidate_id": "anon_005", "score": 65, "metadata": {"gender": "M", "college": "State University", "college_tier": 2, "location": "Bangalore"}, "evidence": {"portfolio_score": 65, "test_score": 68, "interview_signal": 70}},
    
    # Female candidates (intentionally lower scores to simulate bias)
    {"candidate_id": "anon_006", "score": 75, "metadata": {"gender": "F", "college": "IIT Bombay", "college_tier": 1, "location": "Mumbai"}, "evidence": {"portfolio_score": 75, "test_score": None, "interview_signal": 72}},
    {"candidate_id": "anon_007", "score": 68, "metadata": {"gender": "F", "college": "BITS", "college_tier": 1, "location": "Hyderabad"}, "evidence": {"portfolio_score": 68, "test_score": 70, "interview_signal": 65}},
    {"candidate_id": "anon_008", "score": 62, "metadata": {"gender": "F", "college": "Local College", "college_tier": 3, "location": "Pune"}, "evidence": {"portfolio_score": 62, "test_score": 65, "interview_signal": 60}},
    {"candidate_id": "anon_009", "score": 70, "metadata": {"gender": "F", "college": "State University", "college_tier": 2, "location": "Kolkata"}, "evidence": {"portfolio_score": 70, "test_score": 72, "interview_signal": 68}},
    {"candidate_id": "anon_010", "score": 73, "metadata": {"gender": "F", "college": "NIT", "college_tier": 1, "location": "Delhi"}, "evidence": {"portfolio_score": 73, "test_score": None, "interview_signal": 70}},
]

# Run bias audit
print("=" * 60)
print("RUNNING BIAS DETECTION AUDIT")
print("=" * 60)

report = agent.audit_candidates(candidates)
print(json.dumps(report, indent=2))

# Create alert if bias detected
if report["bias_detected"]:
    print("\n" + "=" * 60)
    print("BIAS ALERT GENERATED")
    print("=" * 60)
    alert = agent.create_bias_alert(report)
    print(json.dumps(alert, indent=2))
