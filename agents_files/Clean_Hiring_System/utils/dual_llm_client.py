import os
import json
import logging
import re
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class RegexExtractionClient:
    """
    Pattern-Based Extraction Client (Replacing DualLLMClient)
    
    Uses deterministic regex patterns instead of LLM calls for:
    - Skill extraction
    - Technology identification
    - Experience parsing
    - Project details extraction
    
    Benefits:
    - ~10-15s faster (no API calls)
    - Deterministic results
    - No API costs
    - Works offline
    """
    
    def __init__(self):
        """Initialize regex patterns for extraction"""
        
        # Technology/Skill Patterns
        self.tech_patterns = self._build_tech_patterns()
        
        # Experience Patterns
        self.experience_patterns = self._build_experience_patterns()
        
        # Project Patterns
        self.project_patterns = self._build_project_patterns()
        
        # Date Patterns
        self.date_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*-\s*(?:Present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})'
        
        logger.info("RegexExtractionClient initialized with pattern-based extraction")

    def _build_tech_patterns(self) -> Dict[str, List[str]]:
        """
        Build comprehensive technology detection patterns
        
        Returns dictionary of category -> list of patterns
        """
        return {
            "languages": [
                r'\bPython\b', r'\bJava\b', r'\bJavaScript\b', r'\bTypeScript\b',
                r'\bC\+\+\b', r'\bC#\b', r'\bGo\b', r'\bRust\b', r'\bSQL\b',
                r'\bR\b(?!\w)', r'\bPHP\b', r'\bSwift\b', r'\bKotlin\b',
                r'\bScala\b', r'\bRuby\b', r'\bPerl\b', r'\bBash\b', r'\bShell\b'
            ],
            
            "ml_frameworks": [
                r'\bTensorFlow\b', r'\bPyTorch\b', r'\bKeras\b', r'\bscikit-learn\b',
                r'\bXGBoost\b', r'\bLightGBM\b', r'\bJAX\b', r'\bMXNet\b',
                r'\bCaffe\b', r'\bTheano\b', r'\bHugging\s*Face\b', r'\bTransformers\b',
                r'\bONNX\b', r'\bTensorRT\b', r'\bOpenCV\b'
            ],
            
            "cloud_devops": [
                r'\bKubernetes\b', r'\bDocker\b', r'\bAWS\b', r'\bGCP\b',
                r'\bAzure\b', r'\bTerraform\b', r'\bAnsible\b', r'\bJenkins\b',
                r'\bGitHub\s*Actions\b', r'\bCircleCI\b', r'\bGitLab\s*CI\b',
                r'\bArgoCD\b', r'\bHelm\b', r'\bIstio\b', r'\bPrometheus\b',
                r'\bGrafana\b', r'\bDatadog\b'
            ],
            
            "ml_ops": [
                r'\bMLflow\b', r'\bKubeflow\b', r'\bAirflow\b', r'\bPrefect\b',
                r'\bDVC\b', r'\bWandb\b', r'\bWeights\s*&\s*Biases\b',
                r'\bMLOps\b', r'\bSageMaker\b', r'\bVertex\s*AI\b'
            ],
            
            "web_frameworks": [
                r'\bReact\b', r'\bAngular\b', r'\bVue\.js\b', r'\bNode\.js\b',
                r'\bDjango\b', r'\bFlask\b', r'\bFastAPI\b', r'\bExpress\b',
                r'\bSpring\b', r'\bLaravel\b', r'\bRuby\s*on\s*Rails\b',
                r'\bNext\.js\b', r'\bNuxt\.js\b', r'\bSvelte\b'
            ],
            
            "databases": [
                r'\bPostgreSQL\b', r'\bMySQL\b', r'\bMongoDB\b', r'\bRedis\b',
                r'\bElasticsearch\b', r'\bCassandra\b', r'\bDynamoDB\b',
                r'\bOracle\b', r'\bSQL\s*Server\b', r'\bMariaDB\b',
                r'\bNeo4j\b', r'\bCouchbase\b', r'\bInfluxDB\b'
            ],
            
            "big_data": [
                r'\bSpark\b', r'\bHadoop\b', r'\bKafka\b', r'\bFlink\b',
                r'\bHive\b', r'\bPresto\b', r'\bSnowflake\b', r'\bDatabricks\b',
                r'\bRedshift\b', r'\bBigQuery\b'
            ],
            
            "ml_domains": [
                r'\bNLP\b', r'\bComputer\s*Vision\b', r'\bDeep\s*Learning\b',
                r'\bMachine\s*Learning\b', r'\bReinforcement\s*Learning\b',
                r'\bTime\s*Series\b', r'\bRecommendation\s*Systems?\b',
                r'\bLLM\b', r'\bGPT\b', r'\bBERT\b', r'\bYOLO\b',
                r'\bGAN\b', r'\bCNN\b', r'\bRNN\b', r'\bLSTM\b', r'\bTransformer\b'
            ]
        }

    def _build_experience_patterns(self) -> Dict[str, str]:
        """Build patterns for experience extraction"""
        return {
            "job_title": r'^(?:Senior|Lead|Staff|Principal|Junior|Associate|Chief)?\s*(?:Research\s+)?(?:Scientist|Engineer|Developer|Architect|Manager|Director|Analyst|Consultant).*$',
            "company_indicators": r'(?:Inc\.|LLC|Ltd\.|Corp\.|Corporation|Company|Technologies|Systems|Solutions|Labs)',
            "action_verbs": r'^(Architected|Led|Built|Designed|Implemented|Developed|Deployed|Managed|Created|Established|Optimized|Integrated|Migrated|Reduced|Increased|Improved|Delivered)',
            "metrics": r'\b(\d+(?:\.\d+)?)\s*(%|percent|x|times|reduction|increase|improvement|users|customers|requests|queries|TB|GB|MB|million|billion|thousand)\b'
        }

    def _build_project_patterns(self) -> Dict[str, str]:
        """Build patterns for project extraction"""
        return {
            "project_title": r'^[\w\s\-]+(?:\||–|:)',
            "github_link": r'github\.com/[\w\-]+/[\w\-]+',
            "live_demo": r'(?:demo|live|deployed|production)\s*(?:at|:)?\s*(https?://[\w\.\-/]+)',
            "tech_stack": r'(?:Tech\s*Stack|Technologies|Built\s*with|Using):\s*(.+?)(?:\n|$)'
        }

    def extract_skills(self, text: str) -> List[Dict]:
        """
        Extract skills from text using regex patterns
        
        Args:
            text: Resume text to analyze
            
        Returns:
            List of skill dictionaries with category and confidence
        """
        found_skills = []
        text_lower = text.lower()
        
        for category, patterns in self.tech_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    skill_name = match.group(0).strip()
                    
                    # Calculate confidence based on context
                    confidence = self._calculate_skill_confidence(text, skill_name, match.start())
                    
                    found_skills.append({
                        "skill": skill_name,
                        "category": category,
                        "confidence": confidence,
                        "context": self._extract_context(text, match.start(), match.end())
                    })
        
        # Deduplicate by skill name (case-insensitive)
        seen = {}
        for skill in found_skills:
            key = skill["skill"].lower()
            if key not in seen or skill["confidence"] > seen[key]["confidence"]:
                seen[key] = skill
        
        return list(seen.values())

    def _calculate_skill_confidence(self, text: str, skill: str, position: int) -> str:
        """
        Calculate confidence level for a skill mention
        
        Returns: "high", "medium", or "low"
        """
        # Extract surrounding context (200 chars before and after)
        start = max(0, position - 200)
        end = min(len(text), position + 200)
        context = text[start:end].lower()
        
        # High confidence indicators
        high_indicators = [
            'expert', 'advanced', 'proficient', 'extensive',
            'years of experience', 'led', 'architected', 'designed'
        ]
        
        # Medium confidence indicators
        medium_indicators = [
            'experience with', 'worked with', 'used', 'developed',
            'implemented', 'built', 'created'
        ]
        
        # Low confidence indicators
        low_indicators = [
            'familiar with', 'basic', 'learning', 'exposure to',
            'aware of', 'knowledge of'
        ]
        
        if any(indicator in context for indicator in high_indicators):
            return "high"
        elif any(indicator in context for indicator in low_indicators):
            return "low"
        elif any(indicator in context for indicator in medium_indicators):
            return "medium"
        else:
            # Default: if in skills section = medium, else low
            skills_section = re.search(r'skills?.*?(?:experience|education|projects|$)', 
                                      text[max(0, position-500):position+500], 
                                      re.IGNORECASE | re.DOTALL)
            return "medium" if skills_section else "low"

    def _extract_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Extract surrounding context for a match"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        context = text[context_start:context_end].strip()
        
        # Clean up context
        context = ' '.join(context.split())  # Normalize whitespace
        return context

    def extract_experience(self, text: str) -> List[Dict]:
        """
        Extract work experience from text
        
        Returns list of experience entries with claims
        """
        experiences = []
        
        # Find experience section
        exp_match = re.search(
            r'(?:Professional\s+)?Experience(.+?)(?:Projects?|Education|Skills?|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )
        
        if not exp_match:
            logger.warning("No experience section found")
            return []
        
        exp_section = exp_match.group(1)
        lines = [l.strip() for l in exp_section.split('\n') if l.strip()]
        
        current_exp = None
        
        for i, line in enumerate(lines):
            # Check for job title
            if re.match(self.experience_patterns["job_title"], line, re.IGNORECASE):
                # Save previous experience
                if current_exp:
                    experiences.append(current_exp)
                
                # Extract dates (might be in same line or next line)
                date_match = re.search(self.date_pattern, line)
                if not date_match and i + 1 < len(lines):
                    date_match = re.search(self.date_pattern, lines[i + 1])
                
                current_exp = {
                    "role": line.strip(),
                    "company": "",
                    "timeframe": date_match.group(0) if date_match else "",
                    "claims": []
                }
            
            # Check for company name
            elif current_exp and not current_exp["company"]:
                if re.search(self.experience_patterns["company_indicators"], line, re.IGNORECASE):
                    current_exp["company"] = line.strip()
            
            # Extract responsibility/claim
            elif current_exp and re.match(self.experience_patterns["action_verbs"], line):
                claim = self._parse_claim(line)
                if claim:
                    current_exp["claims"].append(claim)
        
        # Don't forget last experience
        if current_exp:
            experiences.append(current_exp)
        
        return experiences

    def _parse_claim(self, claim_text: str) -> Dict:
        """
        Parse a single claim/responsibility
        
        Extracts:
        - Action taken
        - Technologies used
        - Measurable outcomes
        """
        # Extract technologies mentioned
        technologies = []
        for category, patterns in self.tech_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, claim_text, re.IGNORECASE)
                technologies.extend([m.strip() for m in matches])
        
        # Extract metrics
        metrics = re.findall(self.experience_patterns["metrics"], claim_text, re.IGNORECASE)
        
        # Determine evidence strength
        evidence_strength = "high" if metrics else "medium" if technologies else "weak"
        
        return {
            "action": claim_text.strip(),
            "technology": list(set(technologies)),  # Deduplicate
            "outcome": " ".join([f"{m[0]}{m[1]}" for m in metrics]) if metrics else None,
            "evidence_strength": evidence_strength
        }

    def extract_projects(self, text: str) -> List[Dict]:
        """
        Extract projects from text
        
        Returns list of project entries
        """
        projects = []
        
        # Find projects section
        proj_match = re.search(
            r'(?:Notable\s+)?Projects?(.+?)(?:Experience|Education|Skills?|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )
        
        if not proj_match:
            logger.warning("No projects section found")
            return []
        
        proj_section = proj_match.group(1)
        lines = [l.strip() for l in proj_section.split('\n') if l.strip()]
        
        current_project = None
        
        for line in lines:
            # Check for project title (usually has | or : separator)
            if re.search(r'[\|:–]', line):
                if current_project:
                    projects.append(current_project)
                
                parts = re.split(r'[\|:–]', line, maxsplit=1)
                
                current_project = {
                    "project_name": parts[0].strip(),
                    "description": parts[1].strip() if len(parts) > 1 else "",
                    "claims": []
                }
                
                # Extract GitHub link if present
                github_match = re.search(self.project_patterns["github_link"], line)
                if github_match:
                    current_project["github"] = github_match.group(0)
            
            # Extract bullet points as claims
            elif current_project:
                bullet_clean = re.sub(r'^[•\-\*\+]\s*', '', line).strip()
                if len(bullet_clean) > 15:
                    # Extract technologies from claim
                    technologies = []
                    for category, patterns in self.tech_patterns.items():
                        for pattern in patterns:
                            matches = re.findall(pattern, bullet_clean, re.IGNORECASE)
                            technologies.extend(matches)
                    
                    current_project["claims"].append({
                        "description": bullet_clean,
                        "technologies": list(set(technologies)),
                        "evidence_strength": "medium" if technologies else "weak"
                    })
        
        # Don't forget last project
        if current_project:
            projects.append(current_project)
        
        return projects

    def extract_json(self, text: str) -> Dict:
        """
        Helper to extract JSON from markdown code blocks
        (Kept for compatibility with existing code)
        """
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}

    def extract_all(self, text: str) -> Dict:
        """
        One-shot extraction of all components
        
        Args:
            text: Full resume text
            
        Returns:
            Dictionary with skills, experience, and projects
        """
        logger.info("Starting regex-based extraction...")
        
        result = {
            "skills": self.extract_skills(text),
            "experience": self.extract_experience(text),
            "projects": self.extract_projects(text),
            "extraction_method": "regex_patterns",
            "success": True
        }
        
        logger.info(f"Extracted {len(result['skills'])} skills, "
                   f"{len(result['experience'])} experiences, "
                   f"{len(result['projects'])} projects")
        
        return result


# Backward compatibility wrapper
class DualLLMClient(RegexExtractionClient):
    """
    Backward compatibility wrapper
    
    Replaces LLM calls with regex extraction but maintains
    the same interface as the original DualLLMClient
    """
    
    def __init__(self, openrouter_api_key: Optional[str] = None):
        super().__init__()
        logger.info("DualLLMClient initialized with regex backend (LLM calls disabled)")
    
    def call_ollama(self, prompt: str, system_prompt: str = "") -> Dict:
        """
        Compatibility method - extracts using regex instead of Ollama
        """
        logger.info("Using regex extraction instead of Ollama call")
        
        # Extract the text from the prompt (it's usually wrapped in markers)
        text = self._extract_resume_text(prompt)
        
        try:
            result = self.extract_all(text)
            
            # Format as JSON string for compatibility
            content = json.dumps(result, indent=2)
            
            return {
                "content": content,
                "success": True,
                "model": "regex_patterns"
            }
        except Exception as e:
            logger.error(f"Regex extraction failed: {e}")
            return {
                "content": "",
                "success": False,
                "error": str(e)
            }
    
    def call_openrouter(self, prompt: str, system_prompt: str = "") -> Dict:
        """
        Compatibility method - uses regex instead of OpenRouter
        """
        logger.info("Using regex extraction instead of OpenRouter call")
        return self.call_ollama(prompt, system_prompt)
    
    def _extract_resume_text(self, prompt: str) -> str:
        """Extract resume text from wrapped prompt"""
        # Look for common markers
        markers = [
            ("<<<RESUME_TEXT>>>", "<<<END>>>"),
            ("===== BEGIN CANDIDATE DATA =====", "===== END CANDIDATE DATA ====="),
            ("EXPERIENCE SECTION:", "<<<END>>>")
        ]
        
        for start_marker, end_marker in markers:
            if start_marker in prompt:
                text = prompt.split(start_marker)[1]
                if end_marker in text:
                    text = text.split(end_marker)[0]
                return text.strip()
        
        # If no markers found, return entire prompt
        return prompt
