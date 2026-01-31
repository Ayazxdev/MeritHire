"""
LinkedIn PDF Parser (Redesigned)

Extracts ONLY structured facts from user-provided LinkedIn PDFs.
NO scoring. NO verification. NO judgment.

Outputs:
- experience.timeline (company, role, dates)
- experience.total_years
- experience.consistency (stable/frequent_switches)
- skills.claimed
- identity (name, headline, location)

Source: linkedin_pdf
"""
import logging
import os
import re
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class LinkedInPDFParser:
    """
    Parse LinkedIn PDF exports and extract structured facts.
    
    IMPORTANT: This parser extracts CLAIMS only - no verification.
    Verification happens in the main agent pipeline.
    """
    
    def __init__(self, llm=None):
        """
        Initialize parser.
        
        Args:
            llm: Optional LLM for better structuring (Ollama/OpenAI)
        """
        self.llm = llm
    
    
    # Backward compatibility alias
    def extract_from_pdf(self, pdf_path: str) -> Dict:
        """Alias for parse() - backward compatibility"""
        return self.parse(pdf_path)
    
    def parse(self, pdf_path: str) -> Dict:
        """
        Parse LinkedIn PDF and return structured facts.
        
        Args:
            pdf_path: Path to the LinkedIn PDF file
            
        Returns:
            Dict with experience, skills, identity - FACTS ONLY
        """
        if not os.path.exists(pdf_path):
            logger.error(f"PDF not found: {pdf_path}")
            return self._empty_result("file_not_found")
        
        try:
            import pypdf
            
            # 1. Extract raw text from PDF
            text = self._extract_text(pdf_path)
            logger.info(f"Extracted {len(text)} chars from LinkedIn PDF")
            
            if len(text) < 50:
                return self._empty_result("empty_pdf")
            
            # 2. Structure the data
            if self.llm:
                return self._parse_with_llm(text)
            else:
                return self._parse_with_regex(text)
                
        except ImportError:
            logger.error("pypdf not installed. Run: pip install pypdf")
            return self._empty_result("pypdf_missing")
        except Exception as e:
            logger.error(f"Failed to parse LinkedIn PDF: {e}")
            return self._empty_result("parse_error")
    
    
    def _extract_text(self, pdf_path: str) -> str:
        """Extract raw text from PDF"""
        import pypdf
        
        text = ""
        with open(pdf_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        return text.strip()
    
    
    def _parse_with_llm(self, text: str) -> Dict:
        """
        Use LLM to extract structured facts from LinkedIn PDF text.
        
        Returns ONLY facts - no scoring, no judgment.
        """
        prompt = f"""
Extract structured facts from this LinkedIn Profile PDF text.
ONLY extract what is explicitly stated. Do NOT infer or add anything.

TEXT:
{text[:6000]}

Return ONLY valid JSON (no markdown, no explanation):
{{
  "identity": {{
    "name": "Full Name",
    "headline": "Professional headline/title",
    "location": "City, Country"
  }},
  "experience": [
    {{
      "company": "Company Name",
      "role": "Job Title",
      "start": "YYYY-MM",
      "end": "YYYY-MM or present",
      "employment_type": "Full-time/Part-time/Internship/Contract"
    }}
  ],
  "education": [
    {{
      "school": "University/School Name",
      "degree": "Degree/Certification",
      "field": "Field of Study",
      "year": "YYYY"
    }}
  ],
  "skills": ["Skill1", "Skill2", "Skill3"]
}}
"""
        
        try:
            response = self.llm.invoke(prompt)
            
            # Handle both Ollama (string) and ChatOpenAI (object with .content)
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            # Clean markdown wrappers if present
            content = self._clean_json_response(content)
            
            import json
            data = json.loads(content)
            
            # Build structured output
            return self._build_result(data)
            
        except Exception as e:
            logger.warning(f"LLM parsing failed: {e}. Using regex fallback.")
            return self._parse_with_regex(text)
    
    
    def _parse_with_regex(self, text: str) -> Dict:
        """
        Fallback regex-based parsing for LinkedIn PDFs.
        
        LinkedIn PDFs have specific patterns we can match.
        """
        result = {
            "source": "linkedin_pdf",
            "parse_method": "regex_fallback",
            "identity": self._extract_identity_regex(text),
            "experience": self._build_experience_output([]),
            "skills": {"claimed": self._extract_skills_regex(text)},
            "education": [],
            "raw_text_sample": text[:500]
        }
        
        return result
    
    
    def _extract_identity_regex(self, text: str) -> Dict:
        """Extract name and headline from text"""
        lines = text.split("\n")
        
        name = lines[0].strip() if lines else "Unknown"
        headline = lines[1].strip() if len(lines) > 1 else ""
        
        # Try to find location
        location = ""
        for line in lines[:10]:
            if any(loc in line.lower() for loc in ["india", "usa", "uk", "canada", "delhi", "mumbai", "bangalore"]):
                location = line.strip()
                break
        
        return {
            "name": name,
            "headline": headline,
            "location": location
        }
    
    
    def _extract_skills_regex(self, text: str) -> List[str]:
        """Extract skills mentioned in text"""
        # Common tech skills to look for
        skill_patterns = [
            r"Python", r"JavaScript", r"TypeScript", r"Java", r"C\+\+", r"Go",
            r"React", r"Node\.js", r"Vue", r"Angular", r"Django", r"Flask",
            r"AWS", r"Azure", r"GCP", r"Docker", r"Kubernetes",
            r"Machine Learning", r"Deep Learning", r"TensorFlow", r"PyTorch",
            r"YOLO", r"OpenCV", r"Computer Vision", r"NLP",
            r"PX4", r"MAVSDK", r"ROS", r"Drone", r"UAV",
            r"SQL", r"MongoDB", r"PostgreSQL", r"MySQL",
            r"Git", r"CI/CD", r"Linux"
        ]
        
        found_skills = []
        for pattern in skill_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                # Normalize case
                found_skills.append(pattern.replace(r"\+\+", "++").replace(r"\.", "."))
        
        return list(set(found_skills))
    
    
    def _build_result(self, llm_data: Dict) -> Dict:
        """
        Build final structured output from LLM response.
        
        Format matches the agent's expected schema.
        """
        experience_list = llm_data.get("experience", [])
        
        # Calculate timeline
        timeline = []
        for exp in experience_list:
            timeline.append({
                "company": exp.get("company", "Unknown"),
                "role": exp.get("role", "Unknown"),
                "start": self._normalize_date(exp.get("start", "")),
                "end": self._normalize_date(exp.get("end", "")),
                "employment_type": exp.get("employment_type", "Unknown"),
                "source": "linkedin_pdf"
            })
        
        # Calculate total years
        total_years = self._calculate_total_years(timeline)
        
        # Determine consistency
        consistency = self._determine_consistency(timeline)
        
        return {
            "source": "linkedin_pdf",
            "parse_method": "llm",
            
            "identity": llm_data.get("identity", {}),
            
            "experience": {
                "total_years": round(total_years, 1),
                "consistency": consistency,
                "timeline": timeline
            },
            
            "skills": {
                "claimed": llm_data.get("skills", [])
            },
            
            "education": llm_data.get("education", [])
        }
    
    
    def _build_experience_output(self, timeline: List[Dict]) -> Dict:
        """Build experience output structure"""
        total_years = self._calculate_total_years(timeline)
        consistency = self._determine_consistency(timeline)
        
        return {
            "total_years": round(total_years, 1),
            "consistency": consistency,
            "timeline": timeline
        }
    
    
    def _normalize_date(self, date_str: str) -> str:
        """
        Normalize date to YYYY-MM format.
        
        Handles:
        - "November 2025" -> "2025-11"
        - "2025-11" -> "2025-11"
        - "Present" -> "present"
        - "2025" -> "2025-01"
        """
        if not date_str:
            return ""
        
        date_str = date_str.strip()
        
        # Handle "present"
        if date_str.lower() in ["present", "current", "now"]:
            return "present"
        
        # Already in YYYY-MM format
        if re.match(r"^\d{4}-\d{2}$", date_str):
            return date_str
        
        # Handle "Month YYYY" format
        month_map = {
            "january": "01", "february": "02", "march": "03", "april": "04",
            "may": "05", "june": "06", "july": "07", "august": "08",
            "september": "09", "october": "10", "november": "11", "december": "12",
            "jan": "01", "feb": "02", "mar": "03", "apr": "04",
            "jun": "06", "jul": "07", "aug": "08", "sep": "09",
            "oct": "10", "nov": "11", "dec": "12"
        }
        
        parts = date_str.split()
        if len(parts) == 2:
            month_str = parts[0].lower()
            year_str = parts[1]
            if month_str in month_map and year_str.isdigit():
                return f"{year_str}-{month_map[month_str]}"
        
        # Handle just year
        if date_str.isdigit() and len(date_str) == 4:
            return f"{date_str}-01"
        
        return date_str
    
    
    def _calculate_total_years(self, timeline: List[Dict]) -> float:
        """Calculate total years of experience from timeline"""
        total_months = 0
        now = datetime.now()
        
        for exp in timeline:
            start = exp.get("start", "")
            end = exp.get("end", "")
            
            if not start:
                continue
            
            try:
                # Parse start
                if "-" in start:
                    start_year, start_month = map(int, start.split("-"))
                else:
                    continue
                
                # Parse end
                if end == "present":
                    end_year = now.year
                    end_month = now.month
                elif "-" in end:
                    end_year, end_month = map(int, end.split("-"))
                else:
                    continue
                
                months = (end_year - start_year) * 12 + (end_month - start_month)
                total_months += max(1, months)
                
            except (ValueError, TypeError):
                continue
        
        return total_months / 12
    
    
    def _determine_consistency(self, timeline: List[Dict]) -> str:
        """
        Determine career consistency from timeline.
        
        Returns: "stable" | "moderate" | "frequent_switches"
        """
        if len(timeline) <= 1:
            return "stable"
        elif len(timeline) <= 3:
            return "moderate"
        else:
            return "frequent_switches"
    
    
    def _clean_json_response(self, content: str) -> str:
        """Remove markdown code fences from LLM response"""
        content = content.strip()
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            parts = content.split("```")
            if len(parts) >= 2:
                content = parts[1]
        
        return content.strip()
    
    
    def _empty_result(self, error_reason: str) -> Dict:
        """Return empty result structure with error"""
        return {
            "source": "linkedin_pdf",
            "error": error_reason,
            "identity": {},
            "experience": {
                "total_years": 0,
                "consistency": "unknown",
                "timeline": []
            },
            "skills": {
                "claimed": []
            },
            "education": []
        }


# Convenience function
def parse_linkedin_pdf(pdf_path: str, llm=None) -> Dict:
    """Quick function to parse a LinkedIn PDF"""
    parser = LinkedInPDFParser(llm=llm)
    return parser.parse(pdf_path)


if __name__ == "__main__":
    import sys
    import json
    import argparse
    
    parser = argparse.ArgumentParser(description="Parse LinkedIn PDF")
    parser.add_argument("pdf_path", help="Path to LinkedIn PDF")
    parser.add_argument("--json-only", action="store_true", help="Output only JSON without formatting")
    args = parser.parse_args()
    
    pdf_path = args.pdf_path
    json_only = args.json_only
    
    # Try to load Ollama for better parsing
    llm = None
    try:
        from langchain_ollama import ChatOllama
        llm = ChatOllama(model="qwen2.5:7b", temperature=0)
        if not json_only:
            print("✅ Using Ollama for parsing")
    except:
        if not json_only:
            print("⚠️ Ollama not available, using regex fallback")
    
    result = parse_linkedin_pdf(pdf_path, llm=llm)
    
    # Output JSON
    print(json.dumps(result, indent=2, default=str))
    
    if not json_only:
        print("\n✅ LinkedIn extraction complete")
