# 🗄️ Fair Hiring Pipeline - Database & API Handoff

**For:** DB Team Member
**Stack:** FastAPI + PostgreSQL + SQLAlchemy (Async) + asyncpg + Ed25519
**Goal:** Store, retrieve, and verify Skill Passports and Hiring Evaluations.

---

## ⚡ Quick Reference

### One Command (Pipeline Execution)
```bash
python skill_verification_agent/run_complete_workflow.py --github <USERNAME>
```

### Output Files to Capture
| File | Table to Update |
| :--- | :--- |
| `final_credential.json` | `evaluations` |
| `match_result.json` | `evaluations` |
| `passport_credential.json` | `passports` |

---

## 🧱 Database Tables

### 1. `users`
| Column | Type | Notes |
| :--- | :--- | :--- |
| `user_id` | UUID | PK, auto-generated |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL |
| `password_hash` | VARCHAR(255) | bcrypt |
| `full_name` | VARCHAR(255) | |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() |

---

### 2. `evaluations`
| Column | Type | Notes |
| :--- | :--- | :--- |
| `evaluation_id` | UUID | PK |
| `user_id` | UUID | FK → users |
| `job_id` | VARCHAR(100) | |
| `verified_skills` | JSONB | `{"core": [], "frameworks": []}` |
| `skill_confidence` | INT | 0-100 |
| `signal_strength` | VARCHAR(20) | "strong", "weak", "none" |
| `credential_status` | VARCHAR(50) | "VERIFIED", "PENDING_TEST" |
| `match_score` | INT | 0-100 |
| `match_status` | VARCHAR(50) | "MATCHED", "CONDITIONAL_MATCH", "REJECTED" |
| `decision_reason` | VARCHAR(255) | |
| `match_analysis` | JSONB | Full breakdown |
| `bias_checked` | BOOL | |
| `bias_scope` | VARCHAR(50) | "system_level" |
| `candidate_impact` | VARCHAR(50) | "none" |
| `created_at` | TIMESTAMPTZ | |

---

### 3. `passports` (The Signed Credential)
| Column | Type | Notes |
| :--- | :--- | :--- |
| `credential_id` | VARCHAR(50) | PK, e.g., "cred_abc123" |
| `evaluation_id` | UUID | FK → evaluations, UNIQUE |
| `user_id` | UUID | FK → users |
| `payload_hash` | VARCHAR(66) | SHA256 hex |
| `signature` | VARCHAR(130) | Ed25519 hex |
| `public_key` | VARCHAR(66) | Ed25519 public key hex |
| `public_view` | JSONB | Safe data for display |
| `status` | VARCHAR(20) | "ISSUED", "REVOKED" |
| `issued_at` | TIMESTAMPTZ | |
| `expires_at` | TIMESTAMPTZ | |

---

### 4. `jobs`
| Column | Type | Notes |
| :--- | :--- | :--- |
| `job_id` | VARCHAR(100) | PK |
| `title` | VARCHAR(255) | |
| `required_core` | JSONB | `["python", "system design"]` |
| `required_frameworks` | JSONB | `["fastapi", "aws"]` |
| `min_confidence` | INT | DEFAULT 60 |
| `weight_core` | FLOAT | DEFAULT 0.5 |
| `weight_frameworks` | FLOAT | DEFAULT 0.3 |
| `is_active` | BOOL | DEFAULT TRUE |

---

## 🔐 Ed25519 Signing

### Install
```bash
pip install cryptography
```

### Sign Payload
```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import json, hashlib

def sign_passport(payload: dict, private_key_hex: str):
    canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    payload_hash = hashlib.sha256(canonical.encode()).hexdigest()
    priv = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(private_key_hex))
    sig = priv.sign(canonical.encode())
    return f"0x{payload_hash}", f"0x{sig.hex()}"
```

### Verify Signature
```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def verify_passport(payload: dict, sig_hex: str, pub_hex: str):
    canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_hex))
    sig = bytes.fromhex(sig_hex.replace("0x", ""))
    try:
        pub.verify(sig, canonical.encode())
        return True
    except:
        return False
```

---

## 🚀 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/users` | Register |
| `POST` | `/api/auth/login` | Login → JWT |
| `POST` | `/api/evaluations` | Start evaluation |
| `GET` | `/api/evaluations/{id}` | Get details |
| `POST` | `/api/evaluations/{id}/run` | Run pipeline |
| `GET` | `/api/passports/{credential_id}` | Get passport |
| `GET` | `/verify/{credential_id}` | **PUBLIC** Verify page |

---

## 📦 Env Variables

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/fairhiring
ED25519_PRIVATE_KEY_HEX=<secret>
ED25519_PUBLIC_KEY_HEX=<public>
JWT_SECRET=<random>
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## ✅ Checklist

- [ ] Create `fairhiring` DB
- [ ] Alembic migration
- [ ] User Auth (JWT)
- [ ] Evaluation CRUD
- [ ] Pipeline integration
- [ ] Ed25519 signing
- [ ] `/verify` page
- [ ] CORS setup
