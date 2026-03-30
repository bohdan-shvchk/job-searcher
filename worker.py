#!/usr/bin/env python3
"""
Background worker — runs check_new.py and analyze_new.py every 2 hours.
Deployed as a separate Railway process.
"""

import time
import subprocess
import sys
import os
from datetime import datetime

INTERVAL = 2 * 60 * 60  # 2 hours


def run(script):
    print(f"[{datetime.now().strftime('%H:%M')}] Running {script}...", flush=True)
    result = subprocess.run([sys.executable, script], capture_output=True, text=True)
    if result.stdout:
        print(result.stdout, flush=True)
    if result.stderr:
        print(result.stderr, flush=True)
    print(f"[{datetime.now().strftime('%H:%M')}] Done {script}", flush=True)


if __name__ == "__main__":
    print("Worker started. First run immediately.", flush=True)
    run("check_new.py")
    run("analyze_new.py")

    while True:
        print(f"Sleeping {INTERVAL // 3600}h until next check...", flush=True)
        time.sleep(INTERVAL)
        run("check_new.py")
        run("analyze_new.py")
