"""
Filters and ranks raw job postings:
1. Must look like a fresher/entry-level role (or not explicitly senior)
2. Must match at least one skill keyword
3. Ranked by location preference (remote > hyderabad > bangalore > others)
Also tallies skill-frequency for the trends page.
"""
import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Catches "8+ years", "8 years", "8-10 years", "minimum 5 years", etc.
# Anything requiring >2 years' experience gets excluded, regardless of
# whether the posting also happens to mention "fresher" elsewhere.
EXPERIENCE_PATTERN = re.compile(r"(\d+)\s*\+?\s*(?:-\s*\d+\s*)?\s*years?", re.IGNORECASE)
MAX_ALLOWED_YEARS = 2


def _text_blob(job):
    return f"{job.get('title','')} {job.get('description','')}".lower()


def _requires_too_much_experience(blob):
    for match in EXPERIENCE_PATTERN.finditer(blob):
        years = int(match.group(1))
        if years > MAX_ALLOWED_YEARS:
            return True
    return False


def fresher_level(job):
    """Returns 'explicit' (says fresher/entry-level outright), 'likely'
    (doesn't explicitly say so, but nothing rules it out — no senior
    language, no high experience requirement), or 'excluded' (clearly not
    fresher-suitable). Previously this was a strict yes/no gate requiring
    the literal word "fresher" — that silently dropped legitimate 0-2 year
    roles that just don't phrase it that way. Now both 'explicit' and
    'likely' are kept, tagged, and the dashboard lets you filter between them."""
    blob = _text_blob(job)
    if any(k in blob for k in config.SENIOR_EXCLUDE_KEYWORDS):
        return "excluded"
    if _requires_too_much_experience(blob):
        return "excluded"
    if any(k in blob for k in config.FRESHER_KEYWORDS):
        return "explicit"
    return "likely"


def matched_skills(job):
    blob = _text_blob(job)
    matches = {}
    for group, keywords in config.SKILL_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in blob]
        if hits:
            matches[group] = hits
    return matches


def location_rank(job):
    """Returns the priority index if the job matches an allowed location
    (checking both the location field and the full description, since some
    ATSs put country info only in the description), or None if it doesn't
    match anywhere on the allowlist — or matches but is actually restricted
    to a region you're not in (e.g. "remote, US only")."""
    loc = (job.get("location") or "").lower()
    blob = _text_blob(job)
    combined = f"{loc} {blob}"
    if any(k in combined for k in config.LOCATION_EXCLUDE_KEYWORDS):
        return None
    for i, pref in enumerate(config.LOCATION_PRIORITY):
        if pref in loc or pref in blob:
            return i
    return None


def filter_and_rank(raw_jobs):
    """Returns (filtered_jobs, skill_trend_counts). Every kept job is tagged
    with fresher_level ('explicit' or 'likely') so the dashboard can filter
    between "definitely fresher-labeled" and "probably fine, just doesn't
    say so outright" without needing to re-run the scan."""
    filtered = []
    skill_counts = {}  # keyword -> count across all matched fresher postings

    for job in raw_jobs:
        level = fresher_level(job)
        if level == "excluded":
            continue
        skills = matched_skills(job)
        if not skills:
            continue
        rank = location_rank(job)
        if rank is None:
            continue  # not remote and not India-based — excluded

        for group, hits in skills.items():
            for kw in hits:
                skill_counts[kw] = skill_counts.get(kw, 0) + 1

        job = dict(job)
        job["matched_skills"] = skills
        job["location_rank"] = rank
        job["fresher_level"] = level
        filtered.append(job)

    filtered.sort(key=lambda j: j["location_rank"])
    return filtered, skill_counts
