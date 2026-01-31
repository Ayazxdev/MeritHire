# Passport Agent (Trust Anchor)

**Role:** The Wallet / Trust Anchor
**Version:** V1 (HMAC-SHA256 Signing)

## 🎯 Purpose
The `PassportAgent` is the final step in the pipeline. It takes the evaluated capability (from Matching) and the identity proof (from Skill Agent) and fuses them into an **Immutable, Cryptographically Signed Credential**. 

Think of it as the "DigiLocker for Skills".

## 🧠 Key Logic
1.  **Identity Fusion**: Binds `user_id` (User) + `evaluation_id` (Process) + `verified_skills`.
2.  **Immutability**: Hashes the core data payload (`SHA256`).
3.  **Trust**: Signs the hash using a private key (HMAC-SHA256 simulation).
4.  **Verification**: Generates a public verification URL.

## 📥 Inputs
- **Evaluation Bundle**: A simplified object containing `skill_verification`, `bias_report`, and `match_result`.

## 📤 Output (`passport_credential.json`)
```json
{
  "credential_id": "cred_test_...",
  "verification_url": "https://verifier.fairhiring.network/verify/...",
  "status": "ISSUED",
  "passport_record": {
    "hash": "0x...",
    "signature": "0x...",
    "public_view": {...}
  }
}
```

## 🛠️ Usage

### Run Individually
```bash
# From project root
python passport_agent/agents/passport_agent.py
```
*Note: The standalone run uses a mock bundle for demonstration.*
