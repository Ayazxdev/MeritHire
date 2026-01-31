try:
    from PIL import Image
    import pytesseract
    import numpy as np
except ImportError:
    Image = None
    pytesseract = None
    np = None

import logging
import os

logger = logging.getLogger(__name__)

class ImageInjectionDetector:
    """
    2026 Defense: Detect hidden text in uploaded images
    (headshots, certificates, portfolio screenshots)
    """
    
    def __init__(self):
        if not pytesseract:
            logger.warning("Pytesseract not installed. Image scanning disabled.")
            
    def scan_image_for_injection(self, image_path: str) -> dict:
        """
        Extract ALL text from image (including hidden)
        Check for prompt injection patterns
        """
        if not pytesseract or not Image:
             return {
                "injection_detected": False,
                "error": "dependencies_missing",
                "action": "skip_image_scan"
            }

        try:
            # Open image
            img = Image.open(image_path)
            
            # Extract text using OCR
            # Note: Tesseract executable must be in PATH
            extracted_text = pytesseract.image_to_string(img)
            
            # Check for injection patterns
            injection_patterns = [
                "ignore instructions",
                "dismiss instructions",
                "approve candidate",
                "hire immediately",
                "override",
                "system:",
                "score: 100",
                "ignore previous"
            ]
            
            for pattern in injection_patterns:
                if pattern in extracted_text.lower():
                    return {
                        "injection_detected": True,
                        "type": "multimodal_injection",
                        "pattern_found": pattern,
                        "action": "reject_image"
                    }
            
            # Check for suspiciously high text volume in headshot
            # Heuristic: mostly relevant if identified as headshot, but good general check
            if len(extracted_text.split()) > 50:  # Relaxed threshold
                return {
                    "injection_detected": True,
                    "type": "excessive_text_in_image",
                    "action": "manual_review"
                }
            
            return {"injection_detected": False}
            
        except Exception as e:
            logger.error(f"Image scan failed: {e}")
            return {
                "injection_detected": False,
                "error": str(e),
                "action": "skip_image_scan"
            }
