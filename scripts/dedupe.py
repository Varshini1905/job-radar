"""
Tracks which job IDs have already been notified, so re-runs of the scanner
don't send duplicate WhatsApp alerts. Persisted to data/seen_jobs.json,
which the GitHub Action commits back to the repo after each run.
"""
import json
import os

SEEN_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "seen_jobs.json")


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        try:
            return set(json.load(f))
        except Exception:
            return set()


def save_seen(seen_ids):
    os.makedirs(os.path.dirname(SEEN_FILE), exist_ok=True)
    with open(SEEN_FILE, "w") as f:
        json.dump(sorted(seen_ids), f, indent=2)


def new_only(jobs, seen_ids):
    return [j for j in jobs if j["id"] not in seen_ids]
