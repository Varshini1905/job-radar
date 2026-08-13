"""
Fetches raw job postings from all configured sources.
Returns a list of dicts with a consistent shape:
{
  "id": unique string,
  "source": "greenhouse" | "lever" | "adzuna",
  "company": str,
  "title": str,
  "location": str,
  "url": str,
  "description": str,   # plain text, used for skill/fresher matching
}
"""
import requests
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# (connect_timeout, read_timeout) in seconds — short read timeout so a slow/stuck
# server can't hang the whole scan; we'd rather skip one source than freeze.
TIMEOUT = (5, 8)


def fetch_greenhouse(company_slug):
    jobs = []
    print(f"  checking greenhouse:{company_slug} ...", flush=True)
    try:
        url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs?content=true"
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        for j in data.get("jobs", []):
            jobs.append({
                "id": f"gh_{company_slug}_{j['id']}",
                "source": "greenhouse",
                "company": company_slug,
                "title": j.get("title", ""),
                "location": (j.get("location") or {}).get("name", ""),
                "url": j.get("absolute_url", ""),
                "description": j.get("content", "") or "",
            })
    except Exception as e:
        print(f"[greenhouse:{company_slug}] fetch failed: {e}")
    return jobs


def fetch_lever(company_slug):
    jobs = []
    print(f"  checking lever:{company_slug} ...", flush=True)
    try:
        url = f"https://api.lever.co/v0/postings/{company_slug}?mode=json"
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        for j in data:
            jobs.append({
                "id": f"lv_{company_slug}_{j.get('id')}",
                "source": "lever",
                "company": company_slug,
                "title": j.get("text", ""),
                "location": (j.get("categories") or {}).get("location", ""),
                "url": j.get("hostedUrl", ""),
                "description": j.get("descriptionPlain", "") or "",
            })
    except Exception as e:
        print(f"[lever:{company_slug}] fetch failed: {e}")
    return jobs


def fetch_adzuna(query):
    jobs = []
    if not config.ADZUNA_APP_ID or not config.ADZUNA_APP_KEY:
        return jobs  # not configured yet
    print(f"  checking adzuna: '{query}' ...", flush=True)
    try:
        url = (
            f"https://api.adzuna.com/v1/api/jobs/{config.ADZUNA_COUNTRY}/search/1"
            f"?app_id={config.ADZUNA_APP_ID}&app_key={config.ADZUNA_APP_KEY}"
            f"&results_per_page=20&what={requests.utils.quote(query)}&content-type=application/json"
        )
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        for j in data.get("results", []):
            jobs.append({
                "id": f"adz_{j.get('id')}",
                "source": "adzuna",
                "company": (j.get("company") or {}).get("display_name", "Unknown"),
                "title": j.get("title", ""),
                "location": (j.get("location") or {}).get("display_name", ""),
                "url": j.get("redirect_url", ""),
                "description": j.get("description", "") or "",
            })
    except Exception as e:
        print(f"[adzuna:{query}] fetch failed: {e}")
    return jobs


def fetch_remoteok():
    """RemoteOK — free, no signup, globally remote tech jobs."""
    jobs = []
    print("  checking remoteok ...", flush=True)
    try:
        headers = {"User-Agent": "job-radar-personal-project"}
        resp = requests.get("https://remoteok.com/api", headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        for j in data:
            if not isinstance(j, dict) or "id" not in j:
                continue  # first element is a legal notice, not a job
            raw_loc = (j.get("location") or "").strip()
            # normalize RemoteOK's generic/blank values to "Remote" so it matches
            # the location allowlist; anything more specific (e.g. "USA Only")
            # is left as-is so the filter can correctly exclude it if needed.
            location = "Remote" if raw_loc.lower() in ("", "worldwide", "anywhere") else raw_loc
            jobs.append({
                "id": f"rok_{j.get('id')}",
                "source": "remoteok",
                "company": j.get("company", "Unknown"),
                "title": j.get("position", ""),
                "location": location,
                "url": j.get("url", ""),
                "description": j.get("description", "") or "",
            })
    except Exception as e:
        print(f"[remoteok] fetch failed: {e}")
    return jobs


def fetch_remotive(query):
    """Remotive — free, no signup, globally remote tech jobs, keyword search."""
    jobs = []
    print(f"  checking remotive: '{query}' ...", flush=True)
    try:
        url = f"https://remotive.com/api/remote-jobs?search={requests.utils.quote(query)}"
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        for j in data.get("jobs", []):
            raw_loc = (j.get("candidate_required_location") or "").strip()
            # Remotive uses "Worldwide"/"Anywhere" for true global-remote; anything
            # else (e.g. "USA Only", "UK, Ireland") names specific allowed countries —
            # keep that as-is so the location filter can correctly exclude it if
            # India/Remote isn't among them.
            location = "Remote" if raw_loc.lower() in ("worldwide", "anywhere", "") else raw_loc
            jobs.append({
                "id": f"rmv_{j.get('id')}",
                "source": "remotive",
                "company": j.get("company_name", "Unknown"),
                "title": j.get("title", ""),
                "location": location,
                "url": j.get("url", ""),
                "description": j.get("description", "") or "",
            })
    except Exception as e:
        print(f"[remotive:{query}] fetch failed: {e}")
    return jobs


def fetch_all():
    all_jobs = []
    for slug in config.GREENHOUSE_COMPANIES:
        all_jobs.extend(fetch_greenhouse(slug))
    for slug in config.LEVER_COMPANIES:
        all_jobs.extend(fetch_lever(slug))
    for q in config.ADZUNA_QUERIES:
        all_jobs.extend(fetch_adzuna(q))
    all_jobs.extend(fetch_remoteok())
    for q in config.REMOTIVE_QUERIES:
        all_jobs.extend(fetch_remotive(q))
    return all_jobs


if __name__ == "__main__":
    jobs = fetch_all()
    print(f"Fetched {len(jobs)} raw postings")
