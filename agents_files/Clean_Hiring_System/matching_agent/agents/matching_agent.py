
import json
import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class MatchingAgent:
    """
    Stage 5: Transparent Matching Agent
    
    Responsibilities:
    1. Read verified credential (from correct envelope)
    2. Read bias report (to ensure safety)
    3. Match verified skills against job requirements
    4. Produce Explainable Match Score
    """
    
    def match_candidate(
        self, 
        credential_path: str, 
        bias_report_path: str,
        job_description_path: str,
        context_path: str
    ) -> Dict:
        """
        Run the matching process.
        """
        # 1. Load Context
        context = self._load_json(context_path)
        evaluation_id = context.get("evaluation_id") if context else "unknown"
        
        # 2. Load Credential (Envelope Aware)
        credential_envelope = self._load_json(credential_path)
        if "output" in credential_envelope:
            credential = credential_envelope["output"]
        else:
            credential = credential_envelope
            
        # 3. Load Bias Report
        bias_report = self._load_json(bias_report_path)
        
        # 4. Load Job Description
        job_desc = self._load_json(job_description_path)
        
        logger.info(f"Matching Evaluation {evaluation_id} for Job {job_desc.get('job_id')}")
        
        # Security Gate: Check Bias Report Action
        if bias_report.get("action") in ["pause_for_correction", "human_review"]:
            logger.warning(f"Blocking match due to bias action: {bias_report.get('action')}")
            return {
                "match_status": "BLOCKED",
                "reason": f"Bias Agent Triggered: {bias_report.get('action')}",
                "evaluation_id": evaluation_id
            }
            
        # 5. Calculate Score
        # 5. Calculate Score
        match_analysis = self._calculate_match(credential, job_desc)
        score = match_analysis.pop("final_score") # Remove from analysis (Duplicate removal)
        missing_core = match_analysis["matches"]["missing_core"]
        
        # 6. Determine Match Status (Stricter Logic)
        min_score = job_desc.get("min_confidence_score", 0)
        
        if missing_core:
            match_status = "CONDITIONAL_MATCH"
            decision_reason = f"Missing core requirement: {', '.join(missing_core).title()}"
        elif score >= min_score:
            match_status = "MATCHED"
            decision_reason = "Met all requirements and score threshold"
        else:
            match_status = "REJECTED_LOW_SCORE"
            decision_reason = f"Score {score} below threshold {min_score}"

        # 7. Generate Explanation
        explanation = self._generate_explanation(score, match_analysis, bias_report, decision_reason)
        
        # 8. Construct Result (Corrected Structure)
        result = {
            "evaluation_id": evaluation_id,
            "job_id": job_desc.get("job_id"),
            "match_score": score,
            "match_status": match_status,
            "decision_reason": decision_reason,
            "analysis": match_analysis,
            "explanation": explanation,
            "bias_context": {
                "checked": True,
                "bias_scope": "system_level",
                "candidate_impact": "none",
                "status": "monitored" if bias_report.get("bias_detected") else "cleared"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return result

    def _calculate_match(self, credential: Dict, job: Dict) -> Dict:
        """
        Calculate match score based on Core and Framework skills.
        """
        verified_skills = credential.get("verified_skills", {})
        
        # Flatten and lowercase for matching
        if isinstance(verified_skills, list):
            verified_flat = [s.lower() for s in verified_skills]
            verified_core = verified_flat
            verified_frameworks = []
        else:
            verified_core = [s.lower() for s in verified_skills.get("core", [])]
            verified_frameworks = [s.lower() for s in verified_skills.get("frameworks", [])]
        
        reqs = job.get("requirements", {})
        if not reqs and "required_skills" in job:
            # Fallback to flattened schema sent by orchestrator/pipeline
            req_core = [s.lower().strip() for s in job.get("required_skills", [])]
            req_frameworks = [s.lower().strip() for s in job.get("preferred_skills", [])]
        else:
            req_core = [s.lower().strip() for s in reqs.get("core", [])]
            req_frameworks = [s.lower().strip() for s in reqs.get("frameworks", [])]
        
        # Core Match
        matches_core = [s for s in req_core if s in verified_core]
        score_core = (len(matches_core) / len(req_core)) * 100 if req_core else 100
        
        # Framework Match
        matches_fw = [s for s in req_frameworks if s in verified_frameworks]
        score_fw = (len(matches_fw) / len(req_frameworks)) * 100 if req_frameworks else 100
        
        # Weights
        w_core = job.get("weights", {}).get("core", 0.5)
        w_framework = job.get("weights", {}).get("frameworks", 0.3)
        
        skill_confidence = credential.get("skill_confidence", 0)
        
        # Final Weighted Score
        final_score = (score_core * w_core) + (score_fw * w_framework) + (skill_confidence * 0.2)
        
        return {
            "final_score": round(final_score),
            "breakdown": {
                "core_score": round(score_core),
                "framework_score": round(score_fw),
                "confidence_signal": skill_confidence
            },
            "matches": {
                "core": matches_core,
                "frameworks": matches_fw,
                "missing_core": [s for s in req_core if s not in verified_core],
                "missing_frameworks": [s for s in req_frameworks if s not in verified_frameworks]
            }
        }

    def _generate_explanation(self, score: int, analysis: Dict, bias_report: Dict, decision_reason: str) -> str:
        """
        Generate human-readable explanation.
        """
        text = f"Candidate scored {score}/100. Status: {decision_reason}. "
            
        if bias_report.get("bias_detected"):
            text += "[BIAS AUDIT]: System-level bias signals are being monitored. Individual evaluation remains merit-based."
            
        return text

    def _load_json(self, path: str) -> Dict:
        """Safe JSON load"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {path}: {e}")
            return {}

if __name__ == "__main__":
    # Test Runner
    logging.basicConfig(level=logging.INFO)
    agent = MatchingAgent()
    result = agent.match_candidate(
        "final_credential.json",
        "bias_report.json",
        "matching_agent/data/mock_job_description.json",
        "pipeline_context.json"
    )
    print(json.dumps(result, indent=2))
