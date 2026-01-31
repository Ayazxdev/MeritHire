"""
Evidence Graph Builder (2026 Architecture)

Merges evidence from multiple sources into a unified skill graph.
Works with: GitHub, ATS Resume, LinkedIn, LeetCode, Codeforces

NO SCORING - only aggregates evidence and computes confidence weights
"""
import logging
from typing import Dict, List, Optional, Set
from collections import defaultdict

logger = logging.getLogger(__name__)

# Evidence source weights
EVIDENCE_WEIGHTS = {
    "github": 0.45,
    "ats": 0.25,
    "linkedin": 0.15,
    "leetcode": 0.10,
    "codeforces": 0.10
}

# Confidence thresholds
MIN_SKILL_CONFIDENCE = 0.25  # Skills below this are flagged as weak (was 0.30, too strict)
HIGH_CONFIDENCE_THRESHOLD = 0.70

# Framework keywords that may appear in imports but NOT in language detection
# These should NOT trigger "no code evidence" flags
FRAMEWORK_KEYWORDS = [
    "opencv", "cv2", "px4", "mavsdk", "yolo", "yolov", "react", "gazebo", "ros",
    "tensorflow", "pytorch", "keras", "numpy", "pandas", "flask", "django",
    "node", "express", "vue", "angular", "svelte", "next", "jest"
]


class EvidenceGraphBuilder:
    """
    Builds unified evidence graph from multiple sources.
    """
    
    def __init__(self):
        self.evidence_graph = {
            "skills": {},
            "experience": [],
            "projects": []
        }
        self.weak_signals = []
        self.conflict_flags = []
    
    def build_evidence_graph(
        self,
        ats_output: Optional[Dict] = None,
        linkedin_output: Optional[Dict] = None,
        github_output: Optional[Dict] = None,
        leetcode_output: Optional[Dict] = None,
        codechef_output: Optional[Dict] = None,
        evaluation_id: Optional[str] = None # Added for Identity Separation
    ) -> Dict:
        """
        Build unified evidence graph from all sources.
        
        Args:
            ats_output: Resume data
            linkedin_output: LinkedIn PDF data
            github_output: GitHub analysis
            leetcode_output: LeetCode profile
            codechef_output: Codeforces profile (named codechef for backwards compatibility)
        
        Returns:
            Unified evidence graph with skills, experience, projects
        """
        logger.info("Building evidence graph from multiple sources...")
        
        # Track available sources
        available_sources = []
        if ats_output:
            available_sources.append("ats")
        if linkedin_output:
            available_sources.append("linkedin")
        if github_output:
            available_sources.append("github")
        if leetcode_output:
            available_sources.append("leetcode")
        if codechef_output:
            available_sources.append("codechef")  # Maps to codeforces weight
        
        logger.info(f"Available signals: {', '.join(available_sources)}")
        
        # Extract skills from each source
        if github_output:
            self._add_github_skills(github_output)
        
        if ats_output:
            self._add_ats_skills(ats_output)
        
        if linkedin_output:
            self._add_linkedin_skills(linkedin_output)
        
        if leetcode_output:
            self._add_leetcode_skills(leetcode_output)
        
        if codechef_output:
            self._add_codeforces_skills(codechef_output)
        
        # Extract experience
        if ats_output:
            self._add_ats_experience(ats_output)
        
        if linkedin_output:
            self._add_linkedin_experience(linkedin_output)
        
        # Extract projects
        if ats_output:
            self._add_ats_projects(ats_output)
        
        # Compute confidence for each skill
        self._compute_all_confidences()
        
        # NEW: Expand derived skills (YOLO -> Object Detection)
        self._expand_derived_skills()
        
        # Detect conflicts (ATS/LinkedIn claims without code evidence)
        self._detect_conflicts(github_output, leetcode_output, codechef_output)
        
        skill_count = len(self.evidence_graph["skills"])
        conflict_count = len(self.conflict_flags)
        weak_count = len(self.weak_signals)
        
        logger.info(f"Evidence graph built: {skill_count} skills, {conflict_count} conflicts, {weak_count} weak signals")
        
        return {
            "skills": self.evidence_graph["skills"],
            "experience": self.evidence_graph["experience"],
            "projects": self.evidence_graph["projects"],
            "confidence_controls": {
                "missing_signals": self._get_missing_signals(available_sources),
                "weak_signals": self.weak_signals,
                "conflict_flags": self.conflict_flags
            },
            # ADDED: Include raw signals for portfolio score calculation
            "signals": {
                "github": github_output,
                "ats_resume": ats_output,
                "linkedin": linkedin_output,
                "leetcode": leetcode_output,
                "codeforces": codechef_output
            },
            "evaluation_id": evaluation_id # Correctly Propagated
        }
    
    def _add_skill(self, skill_name: str, source: str, evidence_type: str):
        """
        Add or update a skill in the evidence graph.
        
        Args:
            skill_name: Name of the skill
            source: Source of evidence (github, ats, linkedin, leetcode, codeforces)
            evidence_type: Type of evidence (code_evidence, algorithmic_proof, claim)
        """
        if not skill_name or skill_name.strip() == "":
            return
        
        skill_name = skill_name.strip()
        
        if skill_name not in self.evidence_graph["skills"]:
            self.evidence_graph["skills"][skill_name] = {
                "skill": skill_name,
                "sources": [],
                "evidence_types": [],
                "confidence": 0.0
            }
        
        skill = self.evidence_graph["skills"][skill_name]
        
        # Add source if not already present
        if source not in skill["sources"]:
            skill["sources"].append(source)
        
        # Add evidence type if not already present
        if evidence_type not in skill["evidence_types"]:
            skill["evidence_types"].append(evidence_type)
    
    def _add_github_skills(self, github_output: Dict):
        """Extract skills from GitHub analysis"""
        if not github_output:
            return

        verified_languages = []
        # Format 1: skill_signal.verified_languages
        if "skill_signal" in github_output:
            verified_languages = github_output["skill_signal"].get("verified_languages", [])
        
        # Format 2: frameworks (from github_service.py)
        elif "frameworks" in github_output:
            verified_languages = github_output["frameworks"]

        # Format 3: languages (from github_service.py)
        if "languages" in github_output:
            for lang, pct in github_output["languages"].items():
                if pct >= 10: # Only count significant languages
                    self._add_skill(lang, "github", "code_evidence")
        
        for lang in verified_languages:
            # Handle both string and dict formats
            if isinstance(lang, dict):
                skill_name = lang.get("language", "")
            else:
                skill_name = str(lang)
            
            if skill_name:
                self._add_skill(skill_name, "github", "code_evidence")
        
        # FIX #1: Also extract frameworks from best_repositories
        # This captures languages/frameworks at repo level (e.g., Kavach uses Python)
        skill_signal = github_output.get("skill_signal", {})
        for repo in skill_signal.get("best_repositories", []):
            repo_lang = repo.get("language")
            if repo_lang:
                self._add_skill(repo_lang, "github", "code_evidence")
        
        # FIX #1b: Extract frameworks from profile bio (YOLO, PX4, MAVSDK, OpenCV)
        profile = github_output.get("profile", {})
        bio = profile.get("bio", "") or ""
        bio_lower = bio.lower()
        
        # Known frameworks to extract from bio
        bio_frameworks = [
            ("yolo", "YOLO"), ("px4", "PX4"), ("mavsdk", "MAVSDK"),
            ("opencv", "OpenCV"), ("computer vision", "Computer Vision"),
            ("ros", "ROS"), ("gazebo", "Gazebo")
        ]
        
        for keyword, display_name in bio_frameworks:
            if keyword in bio_lower:
                self._add_skill(display_name, "github", "bio_evidence")

    def _add_ats_skills(self, ats_output: Dict):
        """Extract skills from ATS Resume"""
        if not ats_output:
            return

        # Format 1: skills at top level
        skills_list = ats_output.get("skills", [])
        
        # Format 2: evidence.skills
        if not skills_list and "evidence" in ats_output:
            skills_list = ats_output["evidence"].get("skills", [])
            
        # Format 3: deep_analysis.evidence.skills
        if not skills_list and "analysis" in ats_output:
            deep = ats_output["analysis"].get("deep_analysis", {})
            skills_list = deep.get("evidence", {}).get("skills", [])
        
        for skill_item in skills_list:
            # Handle both formats: dict with "skill" key or plain string
            if isinstance(skill_item, dict):
                skill_name = skill_item.get("skill", "")
            elif isinstance(skill_item, str):
                skill_name = skill_item
            else:
                continue
            
            if skill_name:
                self._add_skill(skill_name, "ats", "claim")
    
    def _add_linkedin_skills(self, linkedin_output: Dict):
        """Extract skills from LinkedIn PDF"""
        # Format 1: skills list at top level (from linkedin_service.py)
        claimed_skills = linkedin_output.get("skills", [])
        
        # Format 2: skills.claimed
        if isinstance(claimed_skills, dict):
            claimed_skills = claimed_skills.get("claimed", [])
        
        for skill_item in claimed_skills:
            # Handle both dict and string formats
            if isinstance(skill_item, dict):
                skill_name = skill_item.get("skill", "") or skill_item.get("name", "")
            elif isinstance(skill_item, str):
                skill_name = skill_item
            else:
                continue
            
            if skill_name:
                self._add_skill(skill_name, "linkedin", "claim")
    
    def _add_leetcode_skills(self, leetcode_output: Dict):
        """Extract skills from LeetCode profile"""
        # LeetCode primarily shows top_language
        top_lang = leetcode_output.get("top_language", "")
        
        if top_lang:
            # Clean up language name (e.g., "Python3" -> "Python")
            clean_lang = top_lang.replace("3", "").replace("++", "++").strip()
            self._add_skill(clean_lang, "leetcode", "algorithmic_proof")
    
    def _add_codeforces_skills(self, codeforces_output: Dict):
        """Extract skills from Codeforces profile"""
        # Codeforces shows top_language
        top_lang = codeforces_output.get("top_language", "")
        
        if top_lang:
            # Language might include version (e.g., "C++14 (GCC 6-32)")
            # Extract just the language part
            clean_lang = top_lang.split("(")[0].strip()
            self._add_skill(clean_lang, "codeforces", "algorithmic_proof")
    
    def _add_ats_experience(self, ats_output: Dict):
        """Extract experience from ATS"""
        experience_list = ats_output.get("experience", [])
        
        for exp in experience_list:
            if isinstance(exp, dict):
                self.evidence_graph["experience"].append({
                    "company": exp.get("company", ""),
                    "role": exp.get("role", ""),
                    "timeframe": exp.get("timeframe", ""),
                    "source": "ats"
                })
    
    def _add_linkedin_experience(self, linkedin_output: Dict):
        """Extract experience from LinkedIn"""
        exp_obj = linkedin_output.get("experience", {})
        
        if isinstance(exp_obj, dict):
            timeline = exp_obj.get("timeline", [])
            for exp in timeline:
                if isinstance(exp, dict):
                    self.evidence_graph["experience"].append({
                        "company": exp.get("company", ""),
                        "role": exp.get("role", ""),
                        "timeframe": exp.get("dates", ""),
                        "source": "linkedin"
                    })
    
    def _add_ats_projects(self, ats_output: Dict):
        """Extract projects from ATS"""
        projects_list = ats_output.get("projects", [])
        
        for proj in projects_list:
            if isinstance(proj, dict):
                self.evidence_graph["projects"].append({
                    "name": proj.get("project_name", ""),
                    "description": proj.get("claims", []),
                    "source": "ats"
                })
    
    def _compute_all_confidences(self):
        """Compute confidence score for all skills"""
        for skill_name, skill_data in self.evidence_graph["skills"].items():
            confidence = self._compute_skill_confidence(skill_data)
            skill_data["confidence"] = round(confidence, 2)
            
            # Flag weak signals
            if confidence < MIN_SKILL_CONFIDENCE:
                self.weak_signals.append(f"{skill_name} (confidence: {confidence:.2f})")
    
    def _compute_skill_confidence(self, skill_data: Dict) -> float:
        """
        Compute confidence for a single skill based on sources.
        
        Confidence = sum of weights for all sources that mention this skill
        """
        confidence = 0.0
        
        for source in skill_data["sources"]:
            # Map codechef to codeforces weight
            weight_key = "codeforces" if source == "codechef" else source
            weight = EVIDENCE_WEIGHTS.get(weight_key, 0.0)
            confidence += weight
        
        return confidence
    
    def _detect_conflicts(self, github_output, leetcode_output, codeforces_output):
        """
        Detect conflicts: skills claimed in ATS/LinkedIn but not in code evidence.
        
        FIX #2: Framework-aware conflict detection.
        - Frameworks (OpenCV, PX4, YOLO) may appear via imports, not repo languages.
        - Only flag LANGUAGES that are claimed but have no code evidence.
        """
        # Build set of skills that have ANY code backing
        code_backed = set()
        
        for skill_name, skill_data in self.evidence_graph["skills"].items():
            sources = skill_data["sources"]
            evidence_types = skill_data.get("evidence_types", [])
            
            # Code evidence includes: github, leetcode, codeforces, codechef
            has_code = any(src in sources for src in ["github", "leetcode", "codeforces", "codechef"])
            
            # Bio evidence also counts (frameworks mentioned in GitHub bio)
            has_bio = "bio_evidence" in evidence_types
            
            if has_code or has_bio:
                code_backed.add(skill_name.lower())
        
        # Only flag claims without code evidence
        for skill_name, skill_data in self.evidence_graph["skills"].items():
            skill_lower = skill_name.lower()
            
            # Already has code backing - skip
            if skill_lower in code_backed:
                continue
            
            sources = skill_data["sources"]
            
            # Only check skills from ATS/LinkedIn (self-attested sources)
            if "ats" not in sources and "linkedin" not in sources:
                continue
            
            # SKIP derived skills (they are inferred, not claimed directly)
            if "ontology_derived" in skill_data["evidence_types"]:
                continue

            # SKIP frameworks - they appear via imports, not language detection
            is_framework = any(fw in skill_lower for fw in FRAMEWORK_KEYWORDS)
            if is_framework:
                continue
            
            # Only flag programming LANGUAGES that are claimed without code evidence
            common_languages = [
                "python", "javascript", "java", "c++", "c#", "c", "typescript",
                "go", "rust", "ruby", "php", "kotlin", "swift", "scala"
            ]
            
            is_language = any(lang == skill_lower or lang in skill_lower for lang in common_languages)
            
            if is_language:
                self.conflict_flags.append({
                    "type": "skill_claim_without_code",
                    "issue": f"'{skill_name}' claimed in resume but no code evidence on GitHub",
                    "severity": "medium"
                })

    def _load_ontology(self) -> Dict:
        """Load skill ontology from knowledge base"""
        import os
        import json
        from pathlib import Path
        
        try:
            # Assume knowledge dir is peer to agents dir
            knowledge_path = Path(__file__).parent.parent / "knowledge" / "skill_ontology.json"
            if knowledge_path.exists():
                with open(knowledge_path, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load ontology: {e}")
        return {}

    def _expand_derived_skills(self):
        """
        Expand atomic skills into derived skills using ontology.
        Example: YOLO (0.9) -> Object Detection (0.9 * 0.8 = 0.72)
        """
        ontology = self._load_ontology()
        if not ontology:
            return

        new_skills = {}
        
        # Iterate over currently verified skills
        for skill_name, skill_data in self.evidence_graph["skills"].items():
            # Skip if confidence is too low
            if skill_data["confidence"] < MIN_SKILL_CONFIDENCE:
                continue

            # Check if skill exists in ontology
            # Try exact match or case-insensitive match
            ontology_entry = ontology.get(skill_name)
            if not ontology_entry:
                # Try finding case-insensitive match
                for key, val in ontology.items():
                    if key.lower() == skill_name.lower():
                        ontology_entry = val
                        break
            
            if ontology_entry and "derived_skills" in ontology_entry:
                parent_confidence = skill_data["confidence"]
                
                for derived_name in ontology_entry["derived_skills"]:
                    # Decay confidence for derived skills
                    derived_confidence = round(parent_confidence * 0.8, 2)
                    
                    # If derived skill already exists (e.g. from ATS), we MUST update it 
                    # to mark it as derived, even if confidence is low. 
                    # This prevents false "missing evidence" conflicts.
                    if derived_name in self.evidence_graph["skills"]:
                        existing = self.evidence_graph["skills"][derived_name]
                        if "ontology_derived" not in existing["evidence_types"]:
                            existing["evidence_types"].append("ontology_derived")
                        if "ontology" not in existing["sources"]:
                            existing["sources"].append("ontology")
                        
                        # Only update confidence if improved
                        if derived_confidence > existing["confidence"]:
                            existing["confidence"] = derived_confidence
                            
                    elif derived_confidence >= MIN_SKILL_CONFIDENCE:
                        # Create new derived skill only if confidence is high enough
                        if derived_name in new_skills:
                            # Update temporarily stored new skill if we found a better source
                            if derived_confidence > new_skills[derived_name]["confidence"]:
                                new_skills[derived_name]["confidence"] = derived_confidence
                        else:
                            new_skills[derived_name] = {
                                "skill": derived_name,
                                "sources": ["ontology"],
                                "evidence_types": ["ontology_derived"],
                                "confidence": derived_confidence,
                                "derived_from": skill_name
                            }
                            logger.info(f"Derived: {derived_name} ({derived_confidence}) from {skill_name}")

        # Add new skills to graph
        self.evidence_graph["skills"].update(new_skills)
    
    def _get_missing_signals(self, available_sources: List[str]) -> List[str]:
        """Identify missing signals"""
        missing = []
        
        if "ats" not in available_sources and "linkedin" not in available_sources:
            missing.append("resume_or_linkedin")
        
        if "github" not in available_sources:
            missing.append("github")
        
        if "leetcode" not in available_sources and "codechef" not in available_sources:
            missing.append("competitive_coding")
        
        return missing
