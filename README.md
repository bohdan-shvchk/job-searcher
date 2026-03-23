# Job Search Automation

Automated job vacancy monitoring with AI-powered analysis and a mobile-first web dashboard.

## What it does

- Monitors Ukrainian job boards (Djinni, DOU, Work.ua) every 2 hours
- AI analyzes each vacancy against your profile (fit score 1-10)
- Web dashboard with filters, search, and delete
- Skips low-score vacancies (score <= 2) automatically
- Free: uses Groq API (Llama 3.3 70B) for analysis

## Quick Start (5 minutes)

### 1. Clone and edit config

```bash
cp -r job-search-template ~/job-search
cd ~/job-search
nano config.py    # <-- Edit YOUR profile, keywords, salary, etc.
```

### 2. Run setup

```bash
python3 setup.py
```

This will:
- Generate `profile.md` from your config
- Create `vacancies.md` with your search URLs
- Install Flask if needed
- Offer to set up systemd (web server) and cron (auto-check)

### 3. First run

```bash
python3 check_new.py     # Find vacancies
python3 analyze_new.py   # Analyze them with AI
```

### 4. Open dashboard

```
http://YOUR_SERVER_IP:8080
```

## What to customize in config.py

| Section | What to change |
|---|---|
| `PROFILE` | Your name, target role, experience, salary range |
| `TARGET` | What you're looking for (bullet points) |
| `NOT_INTERESTED` | What to avoid |
| `FIT_CRITERIA` | Scoring table for AI |
| `KEY_EXPERIENCE` | Your achievements for matching |
| `SEARCH_KEYWORDS` | Search queries for job boards |
| `TITLE_KEYWORDS` | Words that must be in vacancy title |
| `SOURCES` | Job board URLs (change search queries!) |
| `GROQ_API_KEY` | Your free API key from console.groq.com |

## File Structure

```
job-search/
  config.py          # <-- YOUR settings (edit this!)
  setup.py           # Run once after editing config
  app.py             # Web server (Flask)
  index.html         # Dashboard UI
  check_new.py       # Vacancy scraper (cron)
  analyze_new.py     # AI analyzer (Groq)
  profile.md         # Auto-generated from config
  vacancies.md       # Vacancy list (auto-updated)
  analyses.json      # AI analysis results
  check.log          # Scraper log
```

## Examples: config.py for different roles

### Python Developer
```python
SEARCH_KEYWORDS = ["python developer", "backend developer", "django"]
TITLE_KEYWORDS = ["python", "backend", "django", "developer"]
SOURCES = {
    "Djinni": {"enabled": True, "url": "https://djinni.co/jobs/keyword-python/"},
    "DOU": {"enabled": True, "url": "https://jobs.dou.ua/vacancies/?search=Python+Developer"},
    "Work.ua": {"enabled": True, "url": "https://www.work.ua/en/jobs-python+developer/"},
}
```

### UI/UX Designer
```python
SEARCH_KEYWORDS = ["ux designer", "ui designer", "product designer"]
TITLE_KEYWORDS = ["design", "ux", "ui", "product design"]
SOURCES = {
    "Djinni": {"enabled": True, "url": "https://djinni.co/jobs/keyword-ui_ux/"},
    "DOU": {"enabled": True, "url": "https://jobs.dou.ua/vacancies/?search=UI/UX+Designer"},
    "Work.ua": {"enabled": True, "url": "https://www.work.ua/en/jobs-ui+ux+designer/"},
}
```

### DevOps Engineer
```python
SEARCH_KEYWORDS = ["devops", "sre", "platform engineer"]
TITLE_KEYWORDS = ["devops", "sre", "platform", "infrastructure", "cloud"]
SOURCES = {
    "Djinni": {"enabled": True, "url": "https://djinni.co/jobs/keyword-devops/"},
    "DOU": {"enabled": True, "url": "https://jobs.dou.ua/vacancies/?search=DevOps"},
    "Work.ua": {"enabled": True, "url": "https://www.work.ua/en/jobs-devops/"},
}
```

### Data Analyst
```python
SEARCH_KEYWORDS = ["data analyst", "bi analyst", "analytics"]
TITLE_KEYWORDS = ["data", "analyst", "analytics", "bi"]
SOURCES = {
    "Djinni": {"enabled": True, "url": "https://djinni.co/jobs/keyword-data+analyst/"},
    "DOU": {"enabled": True, "url": "https://jobs.dou.ua/vacancies/?search=Data+Analyst"},
    "Work.ua": {"enabled": True, "url": "https://www.work.ua/en/jobs-data+analyst/"},
}
```

## Requirements

- Python 3.8+
- Flask (`pip install flask`)
- Groq API key (free: https://console.groq.com)
- Linux server (Ubuntu recommended) for 24/7 monitoring
  - Also works on Mac/Windows for manual runs

## Manual commands

```bash
# Check for new vacancies now
python3 check_new.py

# Analyze unanalyzed vacancies
python3 analyze_new.py

# Start web server manually
python3 app.py

# View logs
tail -f check.log
```

## License

MIT. Use freely.
