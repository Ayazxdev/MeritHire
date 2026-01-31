# Dual LLM & Human Review Integration Walkthrough

## 1. Overview
We have successfully refactored the Hiring System to implement a **Cost-Optimized Dual LLM Strategy** while establishing a centralized **Human Review Loop** for security and bias events.

### Architecture
-   **Extraction Layer**: Uses **Local Ollama (Llama 3.1)** for 90% of tasks (Parsing, Evidence Extraction). ZERO COST.
-   **Security Layer**: Uses **OpenRouter (Claude 3.5 Sonnet / Haiku)** for `PromptInjectionDefender`. HIGH INTELLIGENCE.
-   **Human Review**: A centralized `HumanReviewService` that captures flags from ATS, Skill, and Bias agents into `human_review_queue.json`.

---

## 2. Key Components Created/Modified

### A. Dual LLM Client (`skill_verification_agent/utils/dual_llm_client.py`)
-   **Purpose**: managing routing between Local and Cloud models.
-   **Configuration**:
    -   `call_ollama()`: Connects to `localhost:11434`.
    -   `call_openrouter()`: Connects to `openrouter.ai`.
    -   **Debug Mode**: Logs interception details to stderr (Console) for visibility.

### B. Prompt Injection Defender (`utils/manipulation_detector.py`)
-   **Refactor**: Switched from `ChatOpenAI` (LangChain) to `DualLLMClient`.
-   **Optimization**: Explicitly uses Cloud Model for security checks.
-   **Fixes**: Handles API Key passing and error logging.

### C. Agent Integrations
1.  **ATS Agent**:
    -   Uses `DualLLMClient` (defaults to Ollama) for extraction.
    -   Uses `PromptInjectionDefender` for security.
2.  **Skill Verification Agent**:
    -   Added **Experience Inflation Detection** (Narrative Fraud).
    -   Connected to `HumanReviewService` for blocking manipulation.
3.  **Bias Detection Agent**:
    -   Connected to `HumanReviewService` for **PII Leaks** and **Systemic Bias**.

---

## 3. How to Verify

### Step 1: Check OpenRouter Usage
Run the pipeline with a resume. Watch the console logs (stderr).

```bash
# Example Output
[DualLLMClient] 🌐 Preparing OpenRouter Call...
[DualLLMClient] Model: anthropic/claude-3-haiku
[DualLLMClient] 🔑 API Key loaded ...
[DualLLMClient] ✅ Success!
```

### Step 2: Check Human Review Queue
Inspect `human_review_queue.json` after a run. You should see events like:
```json
{
  "review_id": "review_8697d8",
  "triggered_by": "ats_evidence_collector",
  "severity": "critical",
  "reason": "Prompt injection detected...",
  "status": "pending"
}
```

### Step 3: Check Cost Savings
-   **Clean Resumes**: Processed entirely on Ollama (Free).
-   **Suspicious Resumes**: Trigger Security Check (Low Cost Haiku/Sonnet).

## 4. Next Steps
-   Build the **Reviewer Dashboard** to process events in `human_review_queue.json`.
-   Run batch tests on diverse resumes to fine-tune sensitivity.
