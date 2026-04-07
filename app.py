#!/usr/bin/env python3
"""Vacancy board web app — carousel UI with analysis scores."""

import re
import os
import json
import csv
import sys
import io
import threading
import subprocess
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import WEB_PORT, WEB_HOST, PAGE_TITLE

from flask import Flask, jsonify, request, send_file, Response

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", "/app/data")
os.makedirs(DATA_DIR, exist_ok=True)
MD_FILE = os.path.join(DATA_DIR, "vacancies.md")
ANALYSES_FILE = os.path.join(DATA_DIR, "analyses.json")
STATUSES_FILE = os.path.join(DATA_DIR, "statuses.json")
COMMENTS_FILE = os.path.join(DATA_DIR, "comments.json")

if not os.path.exists(MD_FILE):
    open(MD_FILE, "w").close()
if not os.path.exists(ANALYSES_FILE):
    with open(ANALYSES_FILE, "w") as f:
        f.write("{}")
if not os.path.exists(STATUSES_FILE):
    with open(STATUSES_FILE, "w") as f:
        f.write("{}")
if not os.path.exists(COMMENTS_FILE):
    with open(COMMENTS_FILE, "w") as f:
        f.write("{}")

INTERVAL = 2 * 60 * 60  # 2 hours

VALID_STATUSES = {"new", "applied", "rejected", "not_suitable", "interview"}


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


def load_statuses():
    if os.path.exists(STATUSES_FILE):
        with open(STATUSES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_statuses(data):
    with open(STATUSES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_comments():
    if os.path.exists(COMMENTS_FILE):
        with open(COMMENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_comments(data):
    with open(COMMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_vacancies():
    if not os.path.exists(MD_FILE):
        return []
    with open(MD_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    analyses = load_analyses()
    statuses = load_statuses()
    comments = load_comments()
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
                "vacancy_status": statuses.get(url, "new"),
                "comment": comments.get(url, ""),
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
        statuses = load_statuses()
        if url in statuses:
            del statuses[url]
            save_statuses(statuses)
        comments = load_comments()
        if url in comments:
            del comments[url]
            save_comments(comments)
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


@app.route("/api/vacancies/status", methods=["PUT"])
def api_set_status():
    data = request.json
    url = data.get("url", "")
    status = data.get("status", "")
    if not url or status not in VALID_STATUSES:
        return jsonify({"ok": False, "error": "invalid"}), 400
    statuses = load_statuses()
    statuses[url] = status
    save_statuses(statuses)
    return jsonify({"ok": True})


@app.route("/api/vacancies/comment", methods=["PUT"])
def api_set_comment():
    data = request.json
    url = data.get("url", "")
    comment = data.get("comment", "")
    if not url:
        return jsonify({"ok": False, "error": "invalid"}), 400
    comments = load_comments()
    if comment:
        comments[url] = comment
    elif url in comments:
        del comments[url]
    save_comments(comments)
    return jsonify({"ok": True})


@app.route("/api/vacancies", methods=["DELETE"])
def api_delete():
    data = request.json
    # bulk delete
    if "urls" in data:
        for url in data["urls"]:
            remove_vacancy(url)
        return jsonify({"ok": True})
    url = data.get("url", "")
    if remove_vacancy(url):
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "not found"}), 404


@app.route("/api/export")
def api_export():
    sections = parse_vacancies()
    analyses = load_analyses()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Title", "URL", "Source", "Date", "Score", "Salary", "Remote", "Type", "Status", "Summary"])

    for section in sections:
        for v in section["items"]:
            writer.writerow([
                v["title"],
                v["url"],
                section["name"],
                v.get("date", ""),
                v.get("score", ""),
                v.get("salary", ""),
                v.get("remote", ""),
                v.get("type", ""),
                v.get("vacancy_status", "new"),
                v.get("summary", ""),
            ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=vacancies.csv"}
    )


t = threading.Thread(target=worker_loop, daemon=True)
t.start()

if __name__ == "__main__":
    app.run(host=WEB_HOST, port=WEB_PORT)
