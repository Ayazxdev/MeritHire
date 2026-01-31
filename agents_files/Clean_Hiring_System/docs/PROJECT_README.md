# Fair Hiring Network - Agent Implementation

**Tagline:** *Fair hiring starts with fair systems. We verify both.*

## 📁 Complete Project Structure

```
Agents/
├── AGENTS.md                        # System specification (source of truth)
├── README.md                        # Original design document
├── PROJECT_README.md               # This file
│
├── skill_verification_agent/        # Agent 2: Multi-Stage Skill Verification
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── skill_verification_agent.py   # Main agent (4 stages)
│   │   └── data_normalizer.py            # GitHub/LeetCode/CodeChef normalization
│   ├── scrapers/
│   │   └── __init__.py                   # Placeholder for scrapers
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── schemas.py                    # Pydantic schemas
│   │   └── scoring.py                    # Portfolio scoring + ATS detection
│   ├── config.py
│   ├── example.py
│   ├── test_agent.py
│   ├── requirements.txt
│   └── .env.example
│
├── company_fairness_agent/          # Agent 1: Company Fairness Verification
│   ├── agents/
│   │   ├── __init__.py
│   │   └── company_fairness_agent.py     # JD bias detection
│   ├── config.py
│   ├── example.py
│   └── requirements.txt
│
├── bias_detection_agent/            # Agent 3: Bias Detection (Meta-Agent)
│   ├── agents/
│   │   ├── __init__.py
│   │   └── bias_detection_agent.py       # Audits other agents
│   ├── config.py
│   ├── example.py
│   └── requirements.txt
│
├── matching_agent/                  # Agent 4: Transparent Matching
│   ├── agents/
│   │   ├── __init__.py
│   │   └── matching_agent.py             # Explainable scoring
│   ├── config.py
│   ├── example.py
│   └── requirements.txt
│
├── passport_agent/                  # Agent 5: Skill Passport
│   ├── agents/
│   │   ├── __init__.py
│   │   └── passport_agent.py             # RSA-2048 signed credentials
│   ├── config.py
│   ├── example.py
│   └── requirements.txt
│
└── orchestration/                   # LangGraph Workflow
    ├── config.py
    ├── state.py                          # HiringState TypedDict
    ├── nodes.py                          # Node functions for each agent
    ├── workflow.py                       # LangGraph graph definition
    ├── example.py                        # Complete workflow demo
    ├── requirements.txt
    └── .env.example
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd orchestration
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your OpenRouter API key
```

### 3. Run Individual Agents

```bash
# Test Skill Verification
cd skill_verification_agent
python example.py

# Test Company Fairness
cd company_fairness_agent
python example.py

# Test Bias Detection
cd bias_detection_agent
python example.py

# Test Matching
cd matching_agent
python example.py

# Test Passport
cd passport_agent
python example.py
```

### 4. Run Complete Workflow

```bash
cd orchestration
python example.py
```

## 🏗️ Agent Summary

| Agent | Purpose | LLM | Key Feature |
|-------|---------|-----|-------------|
| **Company Fairness** | Scan JD for bias | Claude Sonnet | Gendered language detection |
| **Skill Verification** | Verify skills from GitHub/LeetCode | Llama 3.1 8B | 4-stage pipeline |
| **Bias Detection** | Audit other agents | Llama 3.1 70B | Statistical gap analysis |
| **Matching** | Explainable scoring | Gemini Pro 1.5 | Same scorecard both parties |
| **Passport** | Issue credentials | Llama 3.1 8B | RSA-2048 + NFC |

## 🔄 Workflow Flow

```
START 
  → verify_company (score >= 60?) 
    → [REJECT if < 60]
    → anonymize 
      → portfolio_analysis 
        → (if weak) skill_test 
        → aggregate_skills 
          → bias_detection 
            → [ALERT if bias]
            → matching 
              → passport 
                → END
```

## ⚙️ Critical Constraints (From AGENTS.md)

- ✅ No single agent makes final decisions
- ✅ ATS keyword ranking FORBIDDEN
- ✅ Bias findings must be logged
- ✅ Same scorecard for both parties
- ✅ Protocall opt-in, 10% weight max
- ✅ No blockchain (use RSA signatures)

## 📡 Redis Event Channels

| Channel | Payload |
|---------|---------|
| `company_verified` | `{company_id, score, status}` |
| `skill_verified` | `{candidate_id, credential_id}` |
| `bias_alert` | `{severity, report}` **CRITICAL** |
| `match_completed` | `{candidate_id, score, decision}` |
| `credential_issued` | `{credential_id}` |

## 💰 Cost Optimization

- **LLM Caching**: SQLiteCache enabled
- **Progressive Quality**: Cheap models first, expensive if needed
- **Batch Processing**: 5 candidates in 1 call where possible
- **Estimated Total**: ~$3.60 per hackathon session

## 🧪 Testing

```bash
# Unit tests for Skill Verification
cd skill_verification_agent
python -m unittest test_agent

# Run all examples
python -c "
from skill_verification_agent.example import *
from company_fairness_agent.example import *
from bias_detection_agent.example import *
from matching_agent.example import *
from passport_agent.example import *
"
```

## 📋 Next Steps

1. **Add Real Scrapers**: Replace placeholder scrapers with actual GitHub/LeetCode/CodeChef scrapers
2. **PostgreSQL Integration**: Replace in-memory registry with database
3. **Redis Integration**: Implement actual pub/sub for events
4. **API Layer**: Add FastAPI endpoints for each agent
5. **Frontend**: Build React dashboard for admins

---

**Version:** 3.0 Final | **Built with:** LangGraph + OpenRouter + Python 3.11
