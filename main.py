"""
Run this on a schedule (see .github/workflows/scan.yml).
Fetch -> filter -> dedupe -> notify -> update dashboard data files.
"""
import json
import os
from datetime import datetime, timezone

from scripts.fetch_jobs import fetch_all
from scripts.filter_jobs import filter_and_rank
from scripts.dedupe import load_seen, save_seen, new_only
from scripts.notify_whatsapp import notify_all

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def write_json(filename, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, filename), "w") as f:
        json.dump(data, f, indent=2)


def main():
    print("Fetching raw postings...")
    raw_jobs = fetch_all()
    print(f"  {len(raw_jobs)} raw postings fetched")

    print("Filtering for fresher + skill match...")
    filtered_jobs, skill_counts = filter_and_rank(raw_jobs)
    print(f"  {len(filtered_jobs)} postings matched")

    seen = load_seen()
    fresh = new_only(filtered_jobs, seen)
    print(f"  {len(fresh)} are new since last run")

    if fresh:
        print("Sending WhatsApp notifications for new postings...")
        notify_all(fresh)

    # persist seen IDs (all matched jobs, not just fresh, so nothing is re-sent later)
    seen.update(j["id"] for j in filtered_jobs)
    save_seen(seen)

    # --- write dashboard data files ---
    write_json("jobs.json", {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_matched": len(filtered_jobs),
        "jobs": filtered_jobs,
    })

    ranked_skills = sorted(skill_counts.items(), key=lambda kv: kv[1], reverse=True)
    write_json("skills_trends.json", {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "skill_frequency": ranked_skills,
    })

    print("Done.")


if __name__ == "__main__":
    main()
