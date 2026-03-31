#!/usr/bin/env python3
"""
Check job boards for new vacancies based on config.py settings.
Run via cron every 2 hours.
"""

import os
import re
import json
import sys
import urllib.request
import urllib.error
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from config import SOURCES, TITLE_KEYWORDS, GROQ_API_KEY, PROFILE

MD_FILE = os.path.join(BASE_DIR, "vacancies.md")
ANALYSES_FILE = os.path.join(BASE_DIR, "analyses.json")
LOG_FILE = os.path.join(BASE_DIR, "check.log")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def fetch_html(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        log(f"  Fetch error for {url}: {e}")
        return ""


def get_existing_urls():
    if not os.path.exists(MD_FILE):
        return set()
    with open(MD_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    return set(re.findall(r'\((https?://[^)]+)\)', content))


def is_relevant(title):
    t = title.lower()
    return any(kw in t for kw in TITLE_KEYWORDS)


# ============================================================
# PARSERS
# ============================================================

def check_djinni(cfg):
    log("Checking Djinni...")
    existing = get_existing_urls()
    results = []
    seen_urls = set()

    keywords = cfg.get("rss_keywords", ["webflow", "shopify", "frontend", "no-code", "automation"])
    for kw in keywords:
        rss_url = f"https://djinni.co/jobs/feed/?keywords={urllib.request.quote(kw)}"
        xml = fetch_html(rss_url)
        if not xml:
            continue
        for m in re.finditer(r'<link>https://djinni\.co(/jobs/(\d+)-[^<]+)</link>', xml):
            url = f"https://djinni.co{m.group(1)}"
            if url in existing or url in seen_urls:
                continue
            seen_urls.add(url)
            title_m = re.search(r'<title><!\[CDATA\[([^\]]+)\]\]></title>', xml[max(0, m.start()-500):m.start()+200])
            if not title_m:
                title_m = re.search(r'<title>([^<]+)</title>', xml[max(0, m.start()-500):m.start()+200])
            title = title_m.group(1).strip() if title_m else m.group(1)
            if is_relevant(title):
                results.append({"title": title, "url": url, "section": "Djinni.co"})
        time.sleep(2)

    log(f"  Found {len(results)} new on Djinni")
    return results


def check_dou(cfg):
    log("Checking DOU...")
    existing = get_existing_urls()
    results = []
    seen_urls = set()

    for base_url in cfg.get("urls", [cfg.get("url", "")]):
        page = 0
        while True:
            url_page = f"{base_url}&page={page}" if page > 0 else base_url
            html = fetch_html(url_page)
            if not html:
                break
            found_on_page = 0
            for m in re.finditer(
                r'href="(https://jobs\.dou\.ua/companies/[^/]+/vacancies/\d+/)[^"]*"[^>]*>\s*([^<]+)',
                html
            ):
                url = m.group(1)
                title = m.group(2).strip()
                if url in existing or url in seen_urls or not is_relevant(title):
                    continue
                seen_urls.add(url)
                results.append({"title": title, "url": url, "section": "DOU.ua"})
                found_on_page += 1

            for m in re.finditer(
                r'href="(/companies/([^/]+)/vacancies/(\d+)/)[^"]*"[^>]*>\s*([^<]{5,})',
                html
            ):
                url = f"https://jobs.dou.ua{m.group(1)}"
                title = m.group(4).strip()
                if url in existing or url in seen_urls or not is_relevant(title):
                    continue
                seen_urls.add(url)
                results.append({"title": title, "url": url, "section": "DOU.ua"})
                found_on_page += 1

            if found_on_page == 0:
                break
            page += 1
            time.sleep(2)

    log(f"  Found {len(results)} new on DOU")
    return results


def check_workua(cfg):
    log("Checking Work.ua...")
    existing = get_existing_urls()
    results = []
    seen_urls = set()

    for base_url in cfg.get("urls", [cfg.get("url", "")]):
        page = 1
        while True:
            url_page = f"{base_url}?page={page}" if page > 1 else base_url
            html = fetch_html(url_page)
            if not html:
                break
            found_on_page = 0
            for m in re.finditer(r'<a[^>]*href="(/en/jobs/(\d+)/)"[^>]*>\s*([^<]{10,})', html):
                path = m.group(1)
                url = f"https://www.work.ua{path}"
                title = m.group(3).strip()
                if url in existing or url in seen_urls or not is_relevant(title):
                    continue
                seen_urls.add(url)
                results.append({"title": title, "url": url, "section": "Work.ua"})
                found_on_page += 1

            if found_on_page == 0:
                break
            page += 1
            time.sleep(2)

    log(f"  Found {len(results)} new on Work.ua")
    return results


PARSERS = {
    "Djinni": check_djinni,
    "DOU": check_dou,
    "Work.ua": check_workua,
}


# ============================================================
# ANALYSIS & MD FILE
# ============================================================

def add_vacancy_to_md(section_name, title, url):
    with open(MD_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    if url in content:
        log(f"    Skipping duplicate URL: {url}")
        return

    lines = content.split("\n")
    lines = [l + "\n" for l in lines]
    if lines:
        lines[-1] = lines[-1].rstrip("\n") + ("\n" if content.endswith("\n") else "")

    today = datetime.now().strftime("%d.%m")
    new_line = f"- [{title}]({url}) *({today})*\n"

    in_section = False
    insert_idx = None
    for i, line in enumerate(lines):
        if line.strip() == f"## {section_name}":
            in_section = True
            continue
        if in_section:
            if line.startswith("## ") or line.strip() == "---":
                insert_idx = i
                break
            if line.startswith("- ["):
                insert_idx = i + 1

    if insert_idx:
        lines.insert(insert_idx, new_line)
    else:
        new_section = f"\n## {section_name}\n\n{new_line}\n"
        lines.append(new_section)

    with open(MD_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

    # Update date
    with open(MD_FILE, "r", encoding="utf-8") as f:
        c = f.read()
    today_full = datetime.now().strftime("%Y-%m-%d")
    c = re.sub(r"Updated: \d{4}-\d{2}-\d{2}", f"Updated: {today_full}", c)
    with open(MD_FILE, "w", encoding="utf-8") as f:
        f.write(c)


def analyze_vacancy(title, url):
    try:
        from analyze_new import fetch_page, analyze_with_groq
        groq_key = os.environ.get("GROQ_API_KEY", GROQ_API_KEY)
        if not groq_key:
            return None
        profile_path = os.path.join(BASE_DIR, "profile.md")
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = f.read()
        page_text = fetch_page(url)
        return analyze_with_groq(title, url, page_text, profile)
    except Exception as e:
        log(f"  Analysis error: {e}")
        return None


def main():
    log("=" * 50)
    log("Starting vacancy check")
    log("=" * 50)

    all_new = []

    for source_name, cfg in SOURCES.items():
        if not cfg.get("enabled"):
            continue
        parser = PARSERS.get(source_name)
        if not parser:
            log(f"  [WARN] No parser for {source_name}")
            continue
        try:
            results = parser(cfg)
            all_new.extend(results)
            time.sleep(2)
        except Exception as e:
            log(f"  ERROR in {source_name}: {e}")

    # Deduplicate
    seen = set()
    unique = []
    for v in all_new:
        if v["url"] not in seen:
            seen.add(v["url"])
            unique.append(v)
    all_new = unique

    if not all_new:
        log(f"No new vacancies found.")
        return

    # Interleave by source so all sources are represented in the limit
    by_source = {}
    for v in all_new:
        by_source.setdefault(v["section"], []).append(v)
    interleaved = []
    sources_list = list(by_source.values())
    while any(sources_list):
        for src in sources_list:
            if src:
                interleaved.append(src.pop(0))
    all_new = interleaved

    log(f"\nTotal: {len(all_new)} new vacancies.\n")

    analyses = {}
    if os.path.exists(ANALYSES_FILE):
        with open(ANALYSES_FILE, "r", encoding="utf-8") as f:
            analyses = json.load(f)

    added = 0
    for v in all_new:
        log(f"  [{v['section']}] {v['title']}")

        result = analyze_vacancy(v["title"], v["url"])
        if result:
            analyses[v["url"]] = result
            score = result.get('score', '?')
            log(f"    Score: {score}/10")
            if isinstance(score, int) and score <= 2:
                log(f"    Skipping (score too low)")
                continue

        add_vacancy_to_md(v["section"], v["title"], v["url"])
        added += 1
        time.sleep(15)

    with open(ANALYSES_FILE, "w", encoding="utf-8") as f:
        json.dump(analyses, f, ensure_ascii=False, indent=2)

    log(f"\nDone. Added {added} vacancies.")
    log("=" * 50)


if __name__ == "__main__":
    main()
