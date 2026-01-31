# 🤖 AI GitHunter

**AI GitHunter** is an automated recruiting assistant that uses Local LLMs (Ollama) to analyze GitHub profiles and repositories. It goes beyond simple metrics to provide qualitative insights for hiring managers.

### ⚡ What It Can Do

- **Profile Intelligence:** Instead of just counting commits, it uses AI to detect work patterns. It classifies candidates into personas like **"Rising Star"** (inactive start but daily recent activity) or **"Burnout Risk"** (consistent history but stopped recently). It visualizes gaps and calculates a consistency score based on recency.
- **Smart Project Auditing:** It scans repositories to verify if the code matches the `README.md` claims. It detects "Resume Padding" (claiming techs that aren't installed) and identifies "Tutorial Traps" (generic projects copied from YouTube).
- **Dependency Checks:** It cross-references `package.json` or `requirements.txt` with actual file imports to check for bloated or unused libraries.
- **Batch Processing:** You can paste a list of multiple GitHub URLs, and the system will scrape them in parallel (multi-threaded) and generate a comparative report table, saving hours of manual screening.

---

## 🛠️ Environment & Prerequisites

⚠️ **Important:** This project was developed and tested using **Python 3.10**.
All dependencies in `requirements.txt` are locked for this version. Please use Python 3.10 within a virtual environment to avoid conflicts.

**Requirements:**

- Python 3.10
- Chrome Browser (for Selenium scraping)
- **Ollama** (Desktop Application)
- **Model:** `llama3.2`

---

## 📥 Installation

Follow these steps exactly to set up the environment:

**1. Create & Activate Virtual Environment (Python 3.10)**

```bash
# Windows
py -3.10 -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3.10 -m venv venv
source venv/bin/activate

```

**2. Clone the Repository**

```bash
git clone "https://github.com/Udbhaw08/Agents/edit/webScraper"

```

**3. Install Dependencies**

```bash
pip install -r requirements.txt

```

**4. Install & Configure Ollama (First Step)**
You need the Ollama Desktop app running locally to power the AI agent.

1. Download Ollama from [ollama.com](https://ollama.com).
2. Install and run the application.
3. Open your terminal/command prompt and pull the specific model used in this project:

```bash
ollama pull llama3.2

```

_Note: Keep the Ollama app running in the background while using this tool._

---

## 🚀 How to Use

Run the application using Streamlit:

```bash
streamlit run main.py

```

Once the interface opens in your browser, use the three tabs:

1. **👤 Profile Analyzer**

- Paste a GitHub Profile URL (e.g., `https://github.com/torvalds`).
- Click **Analyze Profile** to see the raw data.
- Click **Analyze Consistency (AI Powered)** to let `llama3.2` judge if the candidate is a "Rising Star," "Veteran," or "Sporadic" coder based on their recent streaks.

2. **📂 Project Rater**

- Paste a specific Repository URL (e.g., `https://github.com/username/project`).
- Click **Auto-Analyze Project**. The agent will read the README, scan the `package.json`, and read the `main` code files to give a 0-10 technical score and verify dependencies.

3. **🚀 Batch Processor**

- Paste a list of profile URLs (one per line).
- Click **Analyze All**. The tool will launch parallel scrapers to fetch data quickly and present a comparison table of consistency scores for all candidates.
