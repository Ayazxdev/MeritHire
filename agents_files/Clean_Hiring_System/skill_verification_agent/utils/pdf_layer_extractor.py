import io
import pdfplumber
import fitz  # PyMuPDF

class WhiteTextDetector:
    """
    Detects invisible/white text by comparing rendering layers
    """
    
    def detect_white_text(self, pdf_bytes: bytes) -> dict:
        """
        Compare visible text (rendering) vs all text (extraction)
        Difference = hidden text
        """
        
        # Layer 1: Visible text (what humans see)
        visible_text = self._extract_visible_text(pdf_bytes)
        
        # Layer 2: All text (including invisible)
        all_text = self._extract_all_text(pdf_bytes)
        
        # Find hidden content
        visible_words = set(visible_text.lower().split())
        all_words = set(all_text.lower().split())
        hidden_words = all_words - visible_words
        
        # Analyze suspiciousness
        return self._analyze_hidden_content(hidden_words, all_text)
    
    def _extract_visible_text(self, pdf_bytes: bytes) -> str:
        """
        Extract only visually rendered text
        Uses pdfplumber which respects text rendering
        """
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                visible_text = ""
                for page in pdf.pages:
                    # Extract text with layout awareness
                    text = page.extract_text(
                        layout=True,
                        x_tolerance=3,
                        y_tolerance=3
                    )
                    if text:
                        visible_text += text + "\n"
                
                return visible_text
        except Exception as e:
            # Fallback to all text if rendering fails
            return self._extract_all_text(pdf_bytes)
    
    def _extract_all_text(self, pdf_bytes: bytes) -> str:
        """
        Extract ALL text including invisible layers
        Uses PyMuPDF which gets everything
        """
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            all_text = ""
            for page in doc:
                # Get all text regardless of visibility
                text = page.get_text("text")
                all_text += text + "\n"
            
            doc.close()
            return all_text
        except Exception as e:
            return ""
    
    def _analyze_hidden_content(self, hidden_words: set, full_text: str) -> dict:
        """
        Determine if hidden text is malicious
        """
        
        # Suspicious keywords that shouldn't be hidden
        suspicious_keywords = [
            "hire", "perfect", "candidate", "qualified", "expert",
            "ignore", "instructions", "approve", "score", "100",
            "python", "java", "javascript", "react", "node",  # Tech keywords
            "engineer", "developer", "manager", "lead"  # Titles
        ]
        
        # Find suspicious hidden words
        suspicious_matches = [
            word for word in hidden_words 
            if any(keyword in word.lower() for keyword in suspicious_keywords)
        ]
        
        # Thresholds
        hidden_count = len(hidden_words)
        suspicious_count = len(suspicious_matches)
        
        # Determine severity
        if suspicious_count > 5 or hidden_count > 100:
            severity = "critical"
            action = "immediate_blacklist"
        elif suspicious_count > 2 or hidden_count > 50:
            severity = "high"
            action = "queue_for_review"
        elif hidden_count > 20:
            severity = "medium"
            action = "flag_for_review"
        else:
            severity = "low"
            action = "proceed"
        
        return {
            "white_text_detected": hidden_count > 20,
            "severity": severity,
            "hidden_word_count": hidden_count,
            "suspicious_matches": list(suspicious_matches)[:10],
            "action": action,
            "explanation": f"Found {hidden_count} hidden words, {suspicious_count} suspicious"
        }
