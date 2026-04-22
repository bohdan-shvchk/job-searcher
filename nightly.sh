#!/bin/bash
# Nightly autonomous improvement cycle — runs via cron at 3:00 AM
# Claude Code analyzes the project, picks one improvement, implements it, and logs to changelog.md.
#
# Setup (add to crontab): crontab -e
#   0 3 * * * /path/to/job-searcher/nightly.sh

export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Load .env if present (contains GROQ_API_KEY, etc.)
[ -f "$SCRIPT_DIR/.env" ] && export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)

PROMPT='You are running an autonomous nightly maintenance and improvement cycle for the job-search project. The user has given you FULL autonomy to make decisions and implement changes without asking.

Follow these steps IN ORDER:

## Step 1: Health Check
- Read the current state of all project files (app.py, check_new.py, analyze_new.py, index.html, changelog.html, vacancies.md, analyses.json, changelog.md)
- Run: python3 -c "import app; print(\"OK\")" to check for import/syntax errors
- Run: timeout 120 python3 check_new.py 2>&1 | tail -30
- If there are errors, fix them. After fixing, verify the fix works.

## Step 2: Analyze & Pick One Improvement
Think about what would make this project better. Consider:
- UI/UX improvements to index.html or changelog.html
- Better vacancy parsing/deduplication in check_new.py
- New job board sources
- Better scoring/filtering in analyze_new.py
- Performance, code quality, error handling
- New features (statistics, trends, charts)
- Better data visualization
- Mobile responsiveness improvements
- Remove duplicate vacancies from vacancies.md

Pick ONE concrete improvement that adds the most value. Do NOT repeat improvements already in changelog.md.

## Step 3: Implement the Improvement
Make the code changes. Keep them focused and clean.

## Step 4: Verify
- Run: python3 -c "import app; print(\"OK\")" to verify no import errors
- Check all modified files have valid syntax

## Step 5: Log to Changelog
Append an entry to changelog.md in this format:

---

## YYYY-MM-DD HH:MM

### [Short title of what was done]

**Проблема/Можливість:** [What you identified]

**Рішення:** [What you implemented]

**Змінені файли:** [List of files]

**Перевірка:** [How you verified it works]

---

Write in Ukrainian. Be specific. Do NOT ask the user anything — you have full autonomy.'

claude --dangerously-skip-permissions -p "$PROMPT" \
  --output-format text \
  >> "$SCRIPT_DIR/nightly.log" 2>&1

echo "[$(date)] Nightly run complete" >> "$SCRIPT_DIR/nightly.log"
