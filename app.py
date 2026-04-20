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
CUSTOM_STATUSES_FILE = os.path.join(DATA_DIR, "custom_statuses.json")

for _path, _default in [
    (MD_FILE, None),
    (ANALYSES_FILE, "{}"),
    (STATUSES_FILE, "{}"),
    (COMMENTS_FILE, "{}"),
    (CUSTOM_STATUSES_FILE, "{}"),
]:
    if not os.path.exists(_path):
        with open(_path, "w") as _f:
            if _default is not None:
                _f.write(_default)

INTERVAL = 2 * 60 * 60  # 2 hours

BUILTIN_STATUSES = {
    "new":          {"label": "New",                  "color": "#00a8ff"},
    "applied":      {"label": "Відправив заявку",     "color": "#a29bfe"},
    "interview":    {"label": "Очікування інтерв'ю",  "color": "#ffa502"},
    "rejected":     {"label": "Відмовили",            "color": "#ff4757"},
    "not_suitable": {"label": "Не підходить",         "color": "#777777"},
}


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


def load_custom_statuses():
    if os.path.exists(CUSTOM_STATUSES_FILE):
        with open(CUSTOM_STATUSES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_custom_statuses(data):
    with open(CUSTOM_STATUSES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_all_statuses():
    custom = load_custom_statuses()
    result = {k: {**v, "builtin": True} for k, v in BUILTIN_STATUSES.items()}
    result.update({k: {**v, "builtin": False} for k, v in custom.items()})
    return result


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
        # Статус навмисно не видаляємо — check_new.py перевіряє statuses.json
        # щоб не додавати видалені вакансії знову
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


@app.route("/api/statuses")
def api_get_statuses():
    return jsonify(get_all_statuses())


@app.route("/api/statuses", methods=["POST"])
def api_create_status():
    data = request.json
    label = (data.get("label") or "").strip()
    color = (data.get("color") or "").strip()
    if not label or not re.match(r'^#[0-9a-fA-F]{6}$', color):
        return jsonify({"ok": False, "error": "label and valid hex color required"}), 400
    key = "custom_" + re.sub(r'[^a-z0-9]', '_', label.lower())[:20] + "_" + str(int(time.time()))[-6:]
    custom = load_custom_statuses()
    custom[key] = {"label": label, "color": color}
    save_custom_statuses(custom)
    return jsonify({"ok": True, "key": key})


@app.route("/api/statuses/<key>", methods=["DELETE"])
def api_delete_status(key):
    custom = load_custom_statuses()
    if key not in custom:
        return jsonify({"ok": False, "error": "not found"}), 404
    del custom[key]
    save_custom_statuses(custom)
    statuses = load_statuses()
    changed = False
    for url, s in list(statuses.items()):
        if s == key:
            statuses[url] = "new"
            changed = True
    if changed:
        save_statuses(statuses)
    return jsonify({"ok": True})


@app.route("/api/vacancies/status", methods=["PUT"])
def api_set_status():
    data = request.json
    url = data.get("url", "")
    status = data.get("status", "")
    if not url or status not in get_all_statuses():
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
