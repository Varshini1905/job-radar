"""
Run this any time you add companies to config.py, to check which slugs
are actually valid BEFORE relying on them in the scheduled scan.

Usage: python scripts/verify_companies.py
"""
import sys
import os
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

TIMEOUT = (5, 8)


def check_greenhouse(slug):
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    try:
        r = requests.get(url, timeout=TIMEOUT)
        if r.status_code == 200:
            count = len(r.json().get("jobs", []))
            return True, f"OK — {count} jobs live"
        return False, f"HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)


def check_lever(slug):
    url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    try:
        r = requests.get(url, timeout=TIMEOUT)
        if r.status_code == 200:
            return True, f"OK — {len(r.json())} jobs live"
        return False, f"HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)


def main():
    print("=== Greenhouse ===")
    good_gh, bad_gh = [], []
    for slug in config.GREENHOUSE_COMPANIES:
        ok, msg = check_greenhouse(slug)
        print(f"  {slug:20s} {'✓' if ok else '✗'}  {msg}")
        (good_gh if ok else bad_gh).append(slug)

    print("\n=== Lever ===")
    good_lv, bad_lv = [], []
    for slug in config.LEVER_COMPANIES:
        ok, msg = check_lever(slug)
        print(f"  {slug:20s} {'✓' if ok else '✗'}  {msg}")
        (good_lv if ok else bad_lv).append(slug)

    print("\n=== Summary ===")
    print(f"Valid Greenhouse slugs: {good_gh}")
    print(f"Invalid Greenhouse slugs (remove or fix in config.py): {bad_gh}")
    print(f"Valid Lever slugs: {good_lv}")
    print(f"Invalid Lever slugs (remove or fix in config.py): {bad_lv}")
    print("\nTip: to find a company's real slug, visit their careers page and look")
    print("for a link to boards.greenhouse.io/SLUG or jobs.lever.co/SLUG in the page source,")
    print("or just try https://boards.greenhouse.io/SLUG directly in your browser.")


if __name__ == "__main__":
    main()
