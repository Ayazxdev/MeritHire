# Dual LLM Setup Guide: Ollama + OpenRouter

## 🚀 Quick Setup (5 minutes)

### Step 1: Start Ollama

```bash
# If not installed, install Ollama first
curl -fsSL https://ollama.com/install.sh | sh

# Pull Llama 3.1 (8B for speed, 70B for quality)
ollama pull llama3.1:8b

# Start Ollama server
ollama serve
```

**Test it:**
```bash
# In another terminal
curl http://localhost:11434/api/tags
```

---

### Step 2: Get OpenRouter API Key

1. Go to https://openrouter.ai/
2. Sign up / Log in
3. Go to **Keys** section
4. Create new API key
5. Copy the key (starts with `sk-or-v1-...`)

**Pricing (as of 2024):**
- Claude 3.5 Sonnet: ~$3 per 1M tokens (RECOMMENDED)
- GPT-4 Turbo: ~$10 per 1M tokens
- Gemini Pro: ~$1.25 per 1M tokens
- Mixtral 8x7B: ~$0.50 per 1M tokens

For your use case (100-1000 resumes/month):
- Expected cost: **$5-15/month** with hybrid approach
- All Ollama processing: **$0/month**

---

### Step 3: Set Environment Variable

**Linux/Mac:**
```bash
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"

# Add to ~/.bashrc or ~/.zshrc to make it permanent
echo 'export OPENROUTER_API_KEY="sk-or-v1-your-key-here"' >> ~/.bashrc
```

**Windows (PowerShell):**
```powershell
$env:OPENROUTER_API_KEY="sk-or-v1-your-key-here"

# Permanent:
[System.Environment]::SetEnvironmentVariable('OPENROUTER_API_KEY', 'sk-or-v1-your-key-here', 'User')
```

**Python .env file (alternative):**
```bash
# Create .env file
echo "OPENROUTER_API_KEY=sk-or-v1-your-key-here" > .env

# Install python-dotenv
pip install python-dotenv

# In your code:
from dotenv import load_dotenv
load_dotenv()
```

---

### Step 4: Install Dependencies

```bash
pip install requests python-dotenv
```

---

### Step 5: Test Connection

```bash
python dual_llm_setup_openrouter.py
```

**Expected output:**
```
============================================================
DUAL LLM SETUP TEST
============================================================

1. Testing Ollama...
✅ Ollama is running
Available models: ['llama3.1:8b']

2. Testing OpenRouter...
✅ OpenRouter API key is valid

============================================================
TESTING RESUME PROCESSING
============================================================

--- Processing Clean Resume ---
🔄 Stage 1: Ollama extraction (FREE)...
✅ Clean resume, Ollama-only processing
{
  "extraction": {...},
  "processing_method": "ollama_only",
  "total_cost": 0.0
}

💰 Total cost: $0.0000
```

---

## 🔧 Integration with Your Existing ATS Code

### Option 1: Replace Your Current LLM Calls

Find in your `ats.py`:
```python
# OLD CODE (OpenAI)
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4-turbo")
```

Replace with:
```python
# NEW CODE (Dual LLM)
from dual_llm_setup_openrouter import DualLLMAgent

llm_agent = DualLLMAgent()  # Will auto-detect API key from environment
```

---

### Option 2: Add to Your ATS Agent Class

```python
# In your ats.py file

class ATSAgent:
    def __init__(self):
        # ... your existing code ...
        
        # Add dual LLM
        from dual_llm_setup_openrouter import DualLLMAgent
        self.llm = DualLLMAgent()
    
    def process_resume(self, pdf_path: str) -> dict:
        # Extract text from PDF
        text = self._extract_pdf_text(pdf_path)
        
        # Use dual LLM
        result = self.llm.process_resume(text)
        
        return {
            "extraction": result["extraction"],
            "security_check": result.get("security_check", {}),
            "cost": result["total_cost"],
            "flagged": result["flagged_for_review"]
        }
```

---

## 📊 Cost Optimization Strategy

### When to Use Which LLM

**Use Ollama ONLY (FREE) for:**
- ✅ Initial screening (all resumes)
- ✅ Basic extraction (name, skills, experience)
- ✅ Timeline validation
- ✅ STAR method checking

**Use OpenRouter (PAID) for:**
- ⚠️ Suspicious resumes (Ollama flags something)
- ⚠️ Sophisticated injection detection
- ⚠️ Semantic manipulation analysis
- ⚠️ Final decision on borderline cases

### Expected Costs

**Scenario: 1000 resumes/month**

| Approach | Cost/Month | Detection Rate |
|----------|-----------|----------------|
| Ollama only | $0 | ~85% |
| OpenRouter only | $30-50 | ~95% |
| **Hybrid (RECOMMENDED)** | **$10-15** | **~93%** |

**Breakdown:**
- 1000 resumes → Ollama processes ALL (free)
- ~200 flagged as suspicious (20%)
- 200 × $0.05 = $10 for deep checks

---

## 🎯 Model Selection Guide

Edit `dual_llm_setup_openrouter.py` line 42:

```python
# Choose your cloud model based on budget:

# Best quality (recommended)
self.cloud_model = self.cloud_models["claude"]  # $3/1M tokens

# Cheapest option
self.cloud_model = self.cloud_models["mixtral"]  # $0.50/1M tokens

# Best for coding
self.cloud_model = self.cloud_models["gpt4"]  # $10/1M tokens

# Balanced
self.cloud_model = self.cloud_models["gemini"]  # $1.25/1M tokens
```

---

## 🐛 Troubleshooting

### Issue 1: "Cannot connect to Ollama"

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve

# In another terminal, verify
ollama list
```

---

### Issue 2: "OpenRouter API key not set"

**Solution:**
```bash
# Check if environment variable is set
echo $OPENROUTER_API_KEY  # Linux/Mac
echo $env:OPENROUTER_API_KEY  # Windows

# If empty, set it
export OPENROUTER_API_KEY="your-key-here"
```

---

### Issue 3: "JSON parse error"

**Cause:** LLM returned text instead of pure JSON

**Solution:** The `extract_json()` method handles this automatically, but if you still see errors:

```python
# Add more robust parsing
def extract_json(self, text: str) -> Dict:
    # Try multiple extraction methods
    patterns = [
        r'```json\s*(\{.*?\})\s*```',  # Markdown wrapped
        r'```\s*(\{.*?\})\s*```',       # Generic code block
        r'(\{.*\})',                     # Raw JSON
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                continue
    
    return {}
```

---

### Issue 4: Ollama is slow

**Solutions:**

1. **Use smaller model:**
```bash
ollama pull llama3.1:8b  # Faster, 8GB RAM
# instead of
ollama pull llama3.1:70b  # Slower, needs 48GB RAM
```

2. **Reduce context window:**
```python
# In dual_llm_setup_openrouter.py, line 75
"num_ctx": 2048  # Reduce from 4096
```

3. **Use GPU acceleration:**
```bash
# Check if GPU is detected
ollama list
# Should show "GPU: NVIDIA ..." or "GPU: AMD ..."

# If not detected, reinstall with GPU support
```

---

## 📈 Performance Monitoring

Add this to track costs:

```python
class CostTracker:
    def __init__(self):
        self.total_cost = 0.0
        self.ollama_calls = 0
        self.openrouter_calls = 0
    
    def log(self, result: dict):
        self.total_cost += result.get("total_cost", 0.0)
        if "ollama" in result.get("models_used", []):
            self.ollama_calls += 1
        if "openrouter" in result.get("models_used", []):
            self.openrouter_calls += 1
    
    def report(self):
        print(f"""
Cost Report:
- Total cost: ${self.total_cost:.4f}
- Ollama calls: {self.ollama_calls} (free)
- OpenRouter calls: {self.openrouter_calls} (paid)
- Avg cost per resume: ${self.total_cost / max(1, self.ollama_calls):.4f}
        """)

# Usage
tracker = CostTracker()
for resume in resumes:
    result = agent.process_resume(resume)
    tracker.log(result)

tracker.report()
```

---

## 🔒 Security Best Practices

**Never commit API keys to Git:**

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
echo "config/secrets.py" >> .gitignore
```

**Use environment variables:**

```python
import os
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY not set!")
```

**Rotate keys regularly:**
- Generate new key every 3 months
- Revoke old keys immediately if compromised

---

## ✅ Verification Checklist

- [ ] Ollama is installed and running
- [ ] Llama 3.1 model downloaded (`ollama pull llama3.1:8b`)
- [ ] OpenRouter account created
- [ ] API key obtained and set in environment
- [ ] Dependencies installed (`pip install requests python-dotenv`)
- [ ] Test script runs successfully
- [ ] Both Ollama and OpenRouter connections work
- [ ] Integration with existing ATS code complete

---

## 🎓 Next Steps

1. **Test with your actual resumes**
   ```bash
   python test_dual_llm_with_your_pdfs.py
   ```

2. **Monitor costs for first 100 resumes**
   - Track how many get flagged
   - Adjust sensitivity if needed

3. **Optimize thresholds**
   - Tune when to trigger OpenRouter
   - Balance cost vs accuracy

4. **Add logging**
   - Log all LLM calls
   - Track performance metrics

---

**Questions? Issues?**

Run diagnostics:
```bash
python dual_llm_setup_openrouter.py
```

This will test both connections and show you exactly what's working and what's not.
