# Skill Verification Agent - 2-Step Workflow

## Architecture Overview

```
Step 1: Evidence Collection (Generate JSON files)
     ↓
Step 2: Evidence Processing (Merge → Evaluate → Issue Credential)
```

## Step 1: Generate Evidence Files

Run each scraper individually to generate JSON outputs:

### 1. GitHub Analysis
```bash
cd scraper
python github_api.py USERNAME > ../github_output.json
```

**Output**: `github_output.json`
- Profile data, credibility score
- Best repositories with ownership analysis
- Verified languages
- Commit activity patterns

### 2. ATS Resume Processing
```bash
python agents/ats.py path/to/resume.pdf > ats_output.json
```

**Output**: `ats_output.json`
- Extracted skills
- Experience timeline
- Projects with technologies
- Semantic validation flags

### 3. LinkedIn Processing (Optional)
```bash
python scraper/linkedin_parser.py path/to/linkedin.pdf > linkedin_output.json
```

**Output**: `linkedin_output.json`
- Profile skills
- Experience timeline
- Endorsements

### 4. LeetCode Scraping (Optional)
```bash
python scraper/leetcode_tool.py "https://leetcode.com/u/username/" > leetcode_output.json
```

**Output**: `leetcode_output.json`
- Problems solved
- Contest rating
- Top language
- Difficulty breakdown

### 5. Codeforces Scraping (Optional)
```bash
python scraper/codeforce_tool.py "https://codeforces.com/profile/username" > codeforces_output.json
```

**Output**: `codeforces_output.json`
- Rating, max rating
- Problems solved
- Top language
- Organization

---

## Step 2: Process Evidence & Issue Credential

Once you have the JSON files, run:

```bash
python process_evidence.py
```

This will:
1. ✅ Load all available JSON files
2. ✅ Merge them into an evidence graph
3. ✅ Calculate portfolio scores with trust weights
4. ✅ Issue final credential

**Outputs:**
- `evidence_graph_output.json` - Merged evidence with confidence scores
- `final_credential.json` - Skill credential with verification status

---

## Trust Weight System

```
GitHub:      45%  (Code evidence)
ATS Resume:  25%  (Narrative claims)
LinkedIn:    15%  (Professional profile)
LeetCode:    10%  (Algorithmic proof)
Codeforces:  10%  (Competitive coding)
```

**Auto-normalization**: If a source is missing, weights redistribute proportionally.

Example:
- Only GitHub + ATS → GitHub: 64.3%, ATS: 35.7%
- All 5 sources → Weights as shown above

---

## Signal Strength Rules

```python
if skill_confidence >= 70:
    signal_strength = "strong"
    test_required = False
    
elif 40 <= skill_confidence < 70:
    signal_strength = "weak" 
    test_required = True
    
else:
    signal_strength = "none"
    credential_status = "BLACKLISTED"
```

---

## Example Workflow

```bash
# Step 1: Collect evidence
python scraper/github_api.py Udbhaw08 > github_output.json
python agents/ats.py resume.pdf > ats_output.json
python scraper/leetcode_tool.py "https://leetcode.com/u/example/" > leetcode_output.json
python scraper/codeforce_tool.py "https://codeforces.com/profile/TLE" > codeforces_output.json

# Step 2: Process & evaluate
python process_evidence.py

# View results
cat final_credential.json
```

---

## File Structure

```
skill_verification_agent/
├── process_evidence.py          ← Main processor (Step 2)
├── github_output.json           ← Evidence file
├── ats_output.json              ← Evidence file
├── leetcode_output.json         ← Evidence file
├── codeforces_output.json       ← Evidence file
├── evidence_graph_output.json   ← Generated: Merged evidence
└── final_credential.json        ← Generated: Final result
```

---

## Quick Test

```bash
# If you already have github_output.json and ats_output.json
python process_evidence.py

# Expected output:
# ✅ GitHub
# ✅ ATS Resume  
# 🧠 Building Evidence Graph...
# 🎓 Issuing Skill Credential...
# Status: PROVISIONAL/VERIFIED
# Verified Skills: X
# Skill Confidence: Y
```

---

## Notes

- **Minimum Requirement**: At least 1 code evidence source (GitHub, LeetCode, or Codeforces)
- **ATS/LinkedIn alone**: Cannot add skills, only boost confidence
- **GitHub dominance**: 45% weight ensures code evidence is primary
- **Automatic conflict detection**: Flags skills claimed without code proof
