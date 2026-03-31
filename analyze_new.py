#!/usr/bin/env python3
"""
Analyze vacancies from vacancies.md using Groq API (free Llama 3.3 70B).
Reads profile from profile.md, writes results to analyses.json.
"""

import os
import re
import json
import sys
import urllib.request
import urllib.error
import time
from html.parser import HTMLParser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from config import GROQ_API_KEY, PROFILE, SOURCES

DATA_DIR = os.environ.get("DATA_DIR", "/app/data")
os.makedirs(DATA_DIR, exist_ok=True)
MD_FILE = os.path.join(DATA_DIR, "vacancies.md")
ANALYSES_FILE = os.path.join(DATA_DIR, "analyses.json")
PROFILE_FILE = os.path.join(BASE_DIR, "profile.md")

GROQ_KEY = os.environ.get("GROQ_API_KEY", GROQ_API_KEY)
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# URLs that are aggregate search pages, not individual vacancies
SKIP_PATTERNS = [
    "linkedin.com/jobs", "indeed.com", "glassdoor.com",
    "happymonday.ua", "jobs.dou.ua/vacancies/?search",
]
# Add source search URLs to skip list
for cfg in SOURCES.values():
    if cfg.get("url"):
        SKIP_PATTERNS.append(cfg["url"])


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'nav', 'footer', 'header'):
            self.skip = True

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'nav', 'footer', 'header'):
            self.skip = False

    def handle_data(self, data):
        if not self.skip:
            self.text.append(data.strip())

    def get_text(self):
        return '\n'.join(t for t in self.text if t)


def fetch_page(url):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')
        parser = TextExtractor()
        parser.feed(html)
        text = parser.get_text()
        return text[:5000]
    except Exception as e:
        return f"Failed to fetch: {e}"


def is_aggregate_url(url):
    return any(p in url for p in SKIP_PATTERNS)


def analyze_with_groq(vacancy_title, vacancy_url, page_text, profile):
    if not GROQ_KEY:
        print(f"  [SKIP] No Groq API key")
        return None

    lang = "українською" if PROFILE.get("language", "uk") == "uk" else "in English"

    prompt = f"""Analyze this vacancy for the candidate based on their profile.

PROFILE:
{profile}

VACANCY: {vacancy_title}
URL: {vacancy_url}

PAGE TEXT:
{page_text}

Respond ONLY in JSON format (no markdown, no ```):
{{
  "score": <number 1-10>,
  "summary": "<2-3 sentences {lang}: what company does, why it fits/doesn't fit>",
  "type": "<company type briefly>",
  "salary": "<salary or 'Not specified'>",
  "remote": "<work format>",
  "published": "<vacancy publication date if on the page, format DD.MM.YYYY, or ''>",
  "status": "<'active' if open, 'inactive' if closed/archived>"
}}"""

    body = json.dumps({
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.3,
    }).encode()

    req = urllib.request.Request(GROQ_URL, data=body, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_KEY}",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    })

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
            text = result["choices"][0]["message"]["content"].strip()
            text = re.sub(r'^```json\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            return json.loads(text)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                wait = 30 * (attempt + 1)
                print(f"  [RATE LIMIT] Waiting {wait}s...")
                time.sleep(wait)
                continue
            print(f"  [ERROR] Groq API failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"  [ERROR] Bad JSON from Groq: {e}")
            return None
        except Exception as e:
            print(f"  [ERROR] Groq API failed: {e}")
            return None
    return None


def get_all_vacancy_urls():
    with open(MD_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    vacancies = []
    for m in re.finditer(r"^- \[(.+?)\]\((.+?)\)", content, re.MULTILINE):
        url = m.group(2)
        if not is_aggregate_url(url):
            vacancies.append({"title": m.group(1), "url": url})
    return vacancies


def main():
    if not GROQ_KEY:
        print("ERROR: No Groq API key.")
        print("Get a free key at: https://console.groq.com")
        print("Then set it in config.py or environment: GROQ_API_KEY=gsk_...")
        return

    analyses = {}
    if os.path.exists(ANALYSES_FILE):
        with open(ANALYSES_FILE, "r", encoding="utf-8") as f:
            analyses = json.load(f)

    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        profile = f.read()

    vacancies = get_all_vacancy_urls()
    new_ones = [v for v in vacancies if v["url"] not in analyses]

    if not new_ones:
        print("All vacancies already analyzed.")
        return

    print(f"Found {len(new_ones)} new vacancies to analyze.\n")

    for i, v in enumerate(new_ones, 1):
        print(f"[{i}/{len(new_ones)}] {v['title']}")
        print(f"  Fetching {v['url']}...")
        page_text = fetch_page(v["url"])
        print(f"  Analyzing...")
        result = analyze_with_groq(v["title"], v["url"], page_text, profile)

        if result:
            analyses[v["url"]] = result
            print(f"  Score: {result.get('score', '?')}/10")
            with open(ANALYSES_FILE, "w", encoding="utf-8") as f:
                json.dump(analyses, f, ensure_ascii=False, indent=2)
        else:
            print(f"  [SKIP] No result")

        if i < len(new_ones):
            time.sleep(3)
        print()

    print(f"Done. Total analyzed: {len(analyses)}")


if __name__ == "__main__":
    main()
