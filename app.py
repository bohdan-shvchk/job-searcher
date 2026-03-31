#!/usr/bin/env python3
"""Vacancy board web app — carousel UI with analysis scores."""

import re
import os
import json
import sys
import threading
import subprocess
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import WEB_PORT, WEB_HOST, PAGE_TITLE

from flask import Flask, jsonify, request, send_file

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", "/app/data")
os.makedirs(DATA_DIR, exist_ok=True)
MD_FILE = os.path.join(DATA_DIR, "vacancies.md")
ANALYSES_FILE = os.path.join(DATA_DIR, "analyses.json")
if not os.path.exists(MD_FILE):
    open(MD_FILE, "w").close()
if not os.path.exists(ANALYSES_FILE):
    with open(ANALYSES_FILE, "w") as f:
        f.write("{}")

INTERVAL = 2 * 60 * 60  # 2 hours


def run_script(script):
    print(f"[worker] Running {script}...", flush=True)
    result = subprocess.run([sys.executable, os.path.join(BASE_DIR, script)],
                            capture_output=True, text=True)
    if result.stdout:
        print(result.stdout, flush=True)
    if result.stderr:
        print(result.stderr, flush=True)
    print(f"[worker] Done {script}", flush=True)


def worker_loop():
    run_script("check_new.py")
    run_script("analyze_new.py")
    while True:
        time.sleep(INTERVAL)
        run_script("check_new.py")
        run_script("analyze_new.py")


def load_analyses():
    if os.path.exists(ANALYSES_FILE):
        with open(ANALYSES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_analyses(data):
    with open(ANALYSES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_vacancies():
    if not os.path.exists(MD_FILE):
        return []
    with open(MD_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    analyses = load_analyses()
    sections = []
    current_section = None
    lines = content.split("\n")

    for line in lines:
        h2 = re.match(r"^## (.+)", line)
        if h2:
            current_section = {"name": h2.group(1).strip(), "items": []}
            sections.append(current_section)
            continue

        if current_section is None:
            continue

        m = re.match(r"^- \[(.+?)\]\((.+?)\)\s*(\*\((.+?)\)\*)?", line)
        if m:
            url = m.group(2)
            analysis = analyses.get(url, {})
            current_section["items"].append({
                "title": m.group(1),
                "url": url,
                "date": m.group(4) or "",
                "score": analysis.get("score", None),
                "summary": analysis.get("summary", ""),
                "type": analysis.get("type", ""),
                "salary": analysis.get("salary", ""),
                "remote": analysis.get("remote", ""),
                "published": analysis.get("published", ""),
                "status": analysis.get("status", ""),
            })

    return sections


def remove_vacancy(url):
    if not os.path.exists(MD_FILE):
        return False
    with open(MD_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = [l for l in lines if url not in l]

    if len(new_lines) < len(lines):
        with open(MD_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        analyses = load_analyses()
        if url in analyses:
            del analyses[url]
            save_analyses(analyses)
        return True
    return False


@app.route("/")
def index():
    return send_file("index.html")


@app.route("/api/config")
def api_config():
    return jsonify({"title": PAGE_TITLE})


@app.route("/api/vacancies")
def api_vacancies():
    return jsonify(parse_vacancies())


@app.route("/api/vacancies", methods=["DELETE"])
def api_delete():
    url = request.json.get("url", "")
    if remove_vacancy(url):
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "not found"}), 404


t = threading.Thread(target=worker_loop, daemon=True)
t.start()

if __name__ == "__main__":
    app.run(host=WEB_HOST, port=WEB_PORT)
