# SHEtoken WEI News Agent

Scans 45+ multilingual news sources weekly, classifies articles
using local SLMs (Phi-3.5 Mini + Qwen2.5:3b), and generates
WEI signal reports — emailed to you every Sunday.

---

## How It Works

```
Every Sunday 6am UTC
        ↓
Fetch 45+ RSS feeds (English, Hindi, Bengali,
Urdu, Arabic, Portuguese, Spanish)
        ↓
Pre-filter for WEI keywords
        ↓
Phi-3.5 Mini → English articles
Qwen2.5:3b  → All other languages
        ↓
Each article classified into:
  pillar | direction | severity | confidence
        ↓
Signals aggregated by country/state/pillar
        ↓
→ JSON file (output/signals/)
→ Google Sheets (📡 Weekly Signals tab)
→ Gmail report (HTML email with tables)
```

---

## Quick Start — Local

### 1. Install Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from ollama.com
```

### 2. Pull the SLM models

```bash
ollama pull phi3.5        # ~2.5GB — English classifier
ollama pull qwen2.5:3b    # ~2.0GB — Multilingual classifier
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment

```bash
cp .env.example .env
# Edit .env with your Gmail and Google Sheets credentials
```

**Gmail App Password setup:**
1. Go to myaccount.google.com
2. Security → 2-Step Verification → turn on
3. Security → App passwords
4. Create password for "Mail"
5. Copy the 16-char password to .env

### 5. Run the agent

```bash
# Full run
python run_agent.py

# Dry run (no email/sheets — test only)
python run_agent.py --dry-run

# Scan last 14 days instead of 7
python run_agent.py --days-back 14

# Skip fetching (re-classify cached articles)
python run_agent.py --skip-fetch
```

---

## Deploy to Google Cloud Run

Runs automatically every Sunday. You monitor from anywhere.

### Prerequisites
- Google Cloud account (free tier works)
- gcloud CLI installed: cloud.google.com/sdk

### One-time setup

```bash
# Login to Google Cloud
gcloud auth login
gcloud auth configure-docker us-central1-docker.pkg.dev

# Set your project
export GCP_PROJECT_ID=your-project-id

# Deploy everything
chmod +x deploy.sh
./deploy.sh
```

### What gets created
- **Artifact Registry** — stores the Docker image
- **Cloud Run Job** — runs the agent container
- **Cloud Scheduler** — triggers every Sunday 6am UTC

### Estimated cost
- Cloud Run Job: ~$0.05 per weekly run (8GB RAM, 4 CPU, ~1 hour)
- Cloud Scheduler: Free tier
- Artifact Registry: ~$0.10/month storage
- **Total: ~$0.30/month (~$3.60/year)**

### Monitor from anywhere

```
console.cloud.google.com/run/jobs
```

View logs, execution history, and re-trigger manually.

---

## Output Files

```
output/signals/
├── articles_2025-W20.json    ← cached raw articles
├── signals_2025-W20.json     ← classified signals + report
├── articles_2025-W21.json
└── signals_2025-W21.json
```

### Signal JSON structure

```json
{
  "week": "2025-W20",
  "total_signals": 47,
  "crisis_count": 2,
  "crisis_alerts": [...],
  "global_pillar_summary": {
    "bodily_autonomy": {
      "net_signal": -0.342,
      "total_signals": 12,
      "positive": 3,
      "negative": 9
    }
  },
  "top_movers": [
    {"geo": "IND-WB", "signals": 8, "activity_score": 1.24},
    ...
  ],
  "raw_signals": [...]
}
```

---

## Adding New Sources

Add to `config.py` in NEWS_SOURCES:

```python
("Source Name", "https://example.com/rss.xml", "en", "India", "regional"),
```

Languages: `en` `hi` `bn` `ur` `ar` `pt` `es` `fr`
Regions: any string — used for geography resolution

---

## Troubleshooting

**Ollama not running:**
```bash
ollama serve
```

**Model not found:**
```bash
ollama pull phi3.5
ollama pull qwen2.5:3b
```

**Gmail authentication failed:**
- Make sure you're using an App Password, not your regular password
- 2-Step Verification must be enabled

**No signals classified:**
- Check `agent.log` for errors
- Try `--dry-run` first
- Verify Ollama is running: `curl http://localhost:11434/api/tags`

---

*© 2026 SHE Foundation. MIT License.*
