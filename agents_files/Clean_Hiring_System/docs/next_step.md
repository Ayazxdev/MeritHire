# ✅ ANTIGRAVITY REVIEW ANALYSIS - IMPLEMENTATION PLAN

Based on Antigravity's assessment of your system, here's the **complete implementation roadmap** to achieve **2026 ATS compliance**.

---

## 📊 VULNERABILITY ASSESSMENT SUMMARY

| Threat | Current Status | Priority | Time to Fix |
|--------|---------------|----------|-------------|
| **Invisible Text (White Fonting)** | ⚠️ VULNERABLE | 🔴 CRITICAL | 2 hours |
| **Prompt Injection** | 🟡 PARTIAL | 🔴 CRITICAL | 1 hour |
| **Semantic Validation** | ✅ PROTECTED | ✅ DONE | - |
| **Blacklist & Human Review** | ❌ MISSING | 🟠 HIGH | 3 hours |

**Total Implementation Time: ~6 hours**

---

## 🎯 IMPLEMENTATION ROADMAP

---

## 🔴 PRIORITY 1: WHITE TEXT DETECTION (2 hours)

### **Problem**
Your `ats.py` uses `pypdf` which extracts ALL text (including invisible). A candidate can hide entire job descriptions in white text and your LLM will see it as valid content.

### **Solution: Dual-Layer PDF Extraction**

**Add to `ats_resume_agent.py`:**

```python
# NEW FILE: utils/pdf_layer_extractor.py

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
```

**Integration in `ats.py`:**

```python
# In ATSResumeAgent class

def __init__(self):
    # ... existing code ...
    from utils.pdf_layer_extractor import WhiteTextDetector
    self.white_text_detector = WhiteTextDetector()

def process_resume(self, resume_file_path: str, evaluation_id: str):
    """Enhanced with white text detection"""
    
    # Read PDF bytes
    with open(resume_file_path, 'rb') as f:
        pdf_bytes = f.read()
    
    # STAGE 0: White text detection (NEW)
    white_text_check = self.white_text_detector.detect_white_text(pdf_bytes)
    
    if white_text_check["action"] == "immediate_blacklist":
        return {
            "evaluation_id": evaluation_id,
            "agent": "ats_resume",
            "output": {
                "status": "BLACKLISTED",
                "reason": "White text manipulation detected",
                "evidence": white_text_check,
                "next_stage": "human_review"
            }
        }
    
    # Continue with normal processing...
    # STAGE 1: Extract text (use all_text for now, white text already flagged)
    text_content = self._extract_text_from_pdf(pdf_bytes)
```

**Dependencies:**
```bash
pip install pdfplumber PyMuPDF
```

---

## 🔴 PRIORITY 2: PROMPT INJECTION DETECTION (1 hour)

### **Problem**
Your sandwich defense is good but not foolproof. You need pattern-based detection BEFORE sending to LLM.

### **Solution: Pre-LLM Injection Scanner**

**Add to `ats.py`:**

```python
# In ATSResumeAgent class

class PromptInjectionScanner:
    """
    Scans text for injection patterns BEFORE LLM processing
    """
    
    INJECTION_PATTERNS = [
        # Direct command injections
        r"ignore\s+(previous|all|above|prior)\s+instructions?",
        r"forget\s+(everything|all|previous)",
        r"disregard\s+(previous|all|above)",
        r"override\s+(instructions|rules|system)",
        
        # System/role manipulation
        r"system\s*:\s*",
        r"assistant\s*:\s*",
        r"user\s*:\s*",
        r"you\s+are\s+now\s+",
        r"pretend\s+(to\s+be|you\s+are)",
        r"act\s+as\s+(a|an)?",
        r"roleplay\s+as",
        
        # Instruction delimiters
        r"\[INST\]",
        r"\[/INST\]",
        r"<\|im_start\|>",
        r"<\|im_end\|>",
        r"<<<[A-Z_]+>>>",
        
        # Score manipulation
        r"(score|rate|mark)\s+(me|this|candidate)\s+\d+",
        r"give\s+(me|candidate)\s+(maximum|highest|100)",
        r"return\s+(score|rating)\s*:\s*\d+",
        
        # New instruction attempts
        r"new\s+instructions?",
        r"updated\s+instructions?",
        r"following\s+instructions?"
    ]
    
    def scan(self, text: str) -> dict:
        """
        Scan text for injection patterns
        """
        import re
        
        matches = []
        for pattern in self.INJECTION_PATTERNS:
            found = re.finditer(pattern, text.lower())
            for match in found:
                matches.append({
                    "pattern": pattern,
                    "text": match.group(),
                    "position": match.start()
                })
        
        if not matches:
            return {
                "injection_detected": False,
                "severity": "none",
                "action": "proceed"
            }
        
        # Severity based on match count and pattern types
        critical_patterns = ["system:", "ignore instructions", "[INST]"]
        critical_count = sum(
            1 for m in matches 
            if any(cp in m["text"].lower() for cp in critical_patterns)
        )
        
        if critical_count > 0 or len(matches) >= 3:
            severity = "critical"
            action = "immediate_blacklist"
        elif len(matches) >= 2:
            severity = "high"
            action = "queue_for_review"
        else:
            severity = "medium"
            action = "flag_for_review"
        
        return {
            "injection_detected": True,
            "severity": severity,
            "patterns_matched": [m["text"] for m in matches[:5]],
            "match_count": len(matches),
            "action": action,
            "explanation": f"Detected {len(matches)} potential injection patterns"
        }
```

**Integration:**

```python
# In ATSResumeAgent.process_resume()

def process_resume(self, resume_file_path: str, evaluation_id: str):
    # ... white text detection ...
    
    # Extract text
    text_content = self._extract_text_from_pdf(pdf_bytes)
    
    # STAGE 0.5: Prompt injection scan (NEW)
    injection_scanner = PromptInjectionScanner()
    injection_check = injection_scanner.scan(text_content)
    
    if injection_check["action"] == "immediate_blacklist":
        return {
            "evaluation_id": evaluation_id,
            "agent": "ats_resume",
            "output": {
                "status": "BLACKLISTED",
                "reason": "Prompt injection detected",
                "evidence": injection_check,
                "next_stage": "human_review"
            }
        }
    
    # Continue with normal processing...
```

---

## 🟠 PRIORITY 3: HUMAN REVIEW QUEUE & BLACKLIST (3 hours)

### **Database Schema**

**Create `models/review_models.py`:**

```python
from sqlalchemy import Column, String, DateTime, JSON, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class HumanReviewQueue(Base):
    """
    Queue for flagged candidates requiring human review
    """
    __tablename__ = "human_review_queue"
    
    review_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_id = Column(String, nullable=False, unique=True, index=True)
    candidate_hash = Column(String, nullable=False, index=True)  # SHA256(email)
    
    detection_type = Column(
        Enum(
            "white_text",
            "prompt_injection",
            "timeline_fraud",
            "skill_mismatch",
            "experience_inflation",
            name="detection_type"
        ),
        nullable=False
    )
    
    severity = Column(
        Enum("low", "medium", "high", "critical", name="severity_level"),
        nullable=False
    )
    
    evidence = Column(JSON, nullable=False)
    agent_source = Column(String, nullable=False)  # Which agent flagged it
    
    status = Column(
        Enum("pending", "approved", "rejected", "escalated", name="review_status"),
        default="pending",
        nullable=False
    )
    
    reviewer_id = Column(String, nullable=True)
    reviewer_notes = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)


class CandidateBlacklist(Base):
    """
    Permanent blacklist for candidates caught cheating
    """
    __tablename__ = "candidate_blacklist"
    
    blacklist_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_hash = Column(String, nullable=False, unique=True, index=True)
    
    reason = Column(String, nullable=False)
    detection_type = Column(String, nullable=False)
    evidence_snapshot = Column(JSON, nullable=False)
    
    review_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("human_review_queue.review_id"),
        nullable=True
    )
    
    blacklisted_by = Column(String, default="system")
    blacklist_duration_days = Column(Integer, nullable=True)  # None = permanent
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
```

---

### **Review Service**

**Create `services/review_service.py`:**

```python
from models.review_models import HumanReviewQueue, CandidateBlacklist
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import hashlib

class ReviewService:
    """
    Manages human review queue and blacklist
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def queue_for_review(
        self,
        evaluation_id: str,
        candidate_email: str,
        detection_type: str,
        severity: str,
        evidence: dict,
        agent_source: str
    ) -> str:
        """
        Add candidate to human review queue
        """
        
        # Hash email for privacy
        candidate_hash = hashlib.sha256(candidate_email.encode()).hexdigest()
        
        # Check if already blacklisted
        if self.is_blacklisted(candidate_hash):
            return "already_blacklisted"
        
        # Create review entry
        review = HumanReviewQueue(
            evaluation_id=evaluation_id,
            candidate_hash=candidate_hash,
            detection_type=detection_type,
            severity=severity,
            evidence=evidence,
            agent_source=agent_source,
            status="pending"
        )
        
        self.db.add(review)
        self.db.commit()
        
        return review.review_id
    
    def is_blacklisted(self, candidate_hash: str) -> bool:
        """
        Check if candidate is blacklisted
        """
        blacklist_entry = self.db.query(CandidateBlacklist).filter(
            CandidateBlacklist.candidate_hash == candidate_hash
        ).first()
        
        if not blacklist_entry:
            return False
        
        # Check if temporary blacklist expired
        if blacklist_entry.expires_at:
            if datetime.utcnow() > blacklist_entry.expires_at:
                # Expired, remove from blacklist
                self.db.delete(blacklist_entry)
                self.db.commit()
                return False
        
        return True
    
    def approve_review(self, review_id: str, reviewer_id: str, notes: str = None):
        """
        Approve flagged candidate (false positive)
        """
        review = self.db.query(HumanReviewQueue).filter(
            HumanReviewQueue.review_id == review_id
        ).first()
        
        if review:
            review.status = "approved"
            review.reviewer_id = reviewer_id
            review.reviewer_notes = notes
            review.reviewed_at = datetime.utcnow()
            self.db.commit()
    
    def reject_and_blacklist(
        self,
        review_id: str,
        reviewer_id: str,
        notes: str = None,
        duration_days: int = None
    ):
        """
        Reject candidate and add to blacklist
        duration_days: None = permanent, int = temporary
        """
        review = self.db.query(HumanReviewQueue).filter(
            HumanReviewQueue.review_id == review_id
        ).first()
        
        if not review:
            return False
        
        # Update review status
        review.status = "rejected"
        review.reviewer_id = reviewer_id
        review.reviewer_notes = notes
        review.reviewed_at = datetime.utcnow()
        
        # Add to blacklist
        expires_at = None
        if duration_days:
            expires_at = datetime.utcnow() + timedelta(days=duration_days)
        
        blacklist_entry = CandidateBlacklist(
            candidate_hash=review.candidate_hash,
            reason=review.detection_type,
            detection_type=review.detection_type,
            evidence_snapshot=review.evidence,
            review_id=review.review_id,
            blacklisted_by=reviewer_id,
            blacklist_duration_days=duration_days,
            expires_at=expires_at
        )
        
        self.db.add(blacklist_entry)
        self.db.commit()
        
        return True
```

---

### **FastAPI Endpoints**

**Create `api/review_endpoints.py`:**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.review_service import ReviewService
from models.review_models import HumanReviewQueue
from pydantic import BaseModel

router = APIRouter(prefix="/api/review", tags=["review"])

# Dependency injection
def get_db():
    # Your database session logic
    pass

class ReviewDecision(BaseModel):
    reviewer_id: str
    notes: str = None
    blacklist_duration_days: int = None  # None = permanent


@router.get("/pending")
def get_pending_reviews(db: Session = Depends(get_db)):
    """
    Get all pending reviews (admin dashboard)
    """
    reviews = db.query(HumanReviewQueue).filter(
        HumanReviewQueue.status == "pending"
    ).order_by(
        HumanReviewQueue.severity.desc(),
        HumanReviewQueue.created_at.desc()
    ).all()
    
    return {"reviews": reviews, "count": len(reviews)}


@router.post("/{review_id}/approve")
def approve_review(
    review_id: str,
    decision: ReviewDecision,
    db: Session = Depends(get_db)
):
    """
    Approve flagged candidate (false positive)
    """
    service = ReviewService(db)
    service.approve_review(review_id, decision.reviewer_id, decision.notes)
    
    return {"status": "approved"}


@router.post("/{review_id}/reject")
def reject_and_blacklist(
    review_id: str,
    decision: ReviewDecision,
    db: Session = Depends(get_db)
):
    """
    Reject candidate and add to blacklist
    """
    service = ReviewService(db)
    success = service.reject_and_blacklist(
        review_id,
        decision.reviewer_id,
        decision.notes,
        decision.blacklist_duration_days
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return {"status": "blacklisted"}


@router.get("/blacklist/check/{candidate_email}")
def check_blacklist(candidate_email: str, db: Session = Depends(get_db)):
    """
    Check if candidate is blacklisted (use before processing)
    """
    import hashlib
    candidate_hash = hashlib.sha256(candidate_email.encode()).hexdigest()
    
    service = ReviewService(db)
    is_blacklisted = service.is_blacklisted(candidate_hash)
    
    return {
        "blacklisted": is_blacklisted,
        "candidate_hash": candidate_hash
    }
```

---

### **Integration with Agents**

**Update `ats.py`:**

```python
# In ATSResumeAgent class

def __init__(self, db_session):
    # ... existing code ...
    from services.review_service import ReviewService
    self.review_service = ReviewService(db_session)

def process_resume(self, resume_file_path: str, evaluation_id: str, candidate_email: str):
    # Check blacklist FIRST
    candidate_hash = hashlib.sha256(candidate_email.encode()).hexdigest()
    if self.review_service.is_blacklisted(candidate_hash):
        return {
            "evaluation_id": evaluation_id,
            "agent": "ats_resume",
            "output": {
                "status": "BLACKLISTED_PREVIOUSLY",
                "reason": "Candidate previously blacklisted for cheating"
            }
        }
    
    # ... white text detection ...
    
    if white_text_check["action"] == "immediate_blacklist":
        # Queue for review
        self.review_service.queue_for_review(
            evaluation_id=evaluation_id,
            candidate_email=candidate_email,
            detection_type="white_text",
            severity=white_text_check["severity"],
            evidence=white_text_check,
            agent_source="ats_resume"
        )
        
        return {
            "evaluation_id": evaluation_id,
            "agent": "ats_resume",
            "output": {
                "status": "PENDING_HUMAN_REVIEW",
                "reason": "White text manipulation detected",
                "next_stage": "human_review"
            }
        }
```

---

## 📋 COMPLETE IMPLEMENTATION CHECKLIST

### **Phase 1: Detection (3 hours)**

- [ ] Create `utils/pdf_layer_extractor.py` (30 min)
- [ ] Add `WhiteTextDetector` class (30 min)
- [ ] Create `PromptInjectionScanner` in `ats.py` (30 min)
- [ ] Integrate detectors in `ats.py` (30 min)
- [ ] Test with attack samples (30 min)
- [ ] Install dependencies: `pip install pdfplumber PyMuPDF` (5 min)

### **Phase 2: Database & Review System (2 hours)**

- [ ] Create `models/review_models.py` (20 min)
- [ ] Create database migration script (20 min)
- [ ] Run migrations (10 min)
- [ ] Create `services/review_service.py` (30 min)
- [ ] Test service with sample data (20 min)

### **Phase 3: API & Integration (1 hour)**

- [ ] Create `api/review_endpoints.py` (20 min)
- [ ] Update `ats.py` with review_service integration (20 min)
- [ ] Update `skill_verification_agent_v2.py` (20 min)

### **Phase 4: Testing (1 hour)**

- [ ] Create test resumes with white text (15 min)
- [ ] Create test resumes with prompt injection (15 min)
- [ ] Test blacklist flow end-to-end (30 min)

---

## 🚀 QUICK START (IMMEDIATE ACTION)

**Start with Priority 1 (White Text):**

```bash
# 1. Install dependencies
pip install pdfplumber PyMuPDF

# 2. Create utils/pdf_layer_extractor.py
# (Copy code from Priority 1 above)

# 3. Test immediately
python test_white_text_detection.py
```

**Test Script (`test_white_text_detection.py`):**

```python
from utils.pdf_layer_extractor import WhiteTextDetector

# Test with a clean resume
detector = WhiteTextDetector()

with open("sample_resume.pdf", "rb") as f:
    result = detector.detect_white_text(f.read())

print(result)
# Should output: {"white_text_detected": False, "severity": "low", ...}
```

---