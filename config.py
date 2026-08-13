"""
Central configuration for the job tracker.
Edit this file to add/remove companies, skills, or locations — no need to touch the scanning logic.
"""

# --- 1. GREENHOUSE / LEVER COMPANIES ---------------------------------------
# These are companies known to use Greenhouse or Lever's PUBLIC job board API
# (no auth needed, no ToS issue). Company slugs drift over time (companies
# rename boards or switch ATS providers entirely), so this list WILL go stale.
#
# Run `python scripts/verify_companies.py` any time to see which slugs are
# currently live and which have broken. Fix/remove the broken ones, and find
# new slugs by checking a company's careers page for a boards.greenhouse.io/SLUG
# or jobs.lever.co/SLUG link (view page source if it's not obvious).
#
# NOTE: most companies on public Greenhouse/Lever boards are global/US product
# companies, not India-specific ones. For India/Hyderabad-heavy coverage,
# Adzuna (configured below) is doing most of the real work — this list is a
# bonus source, not the primary one.
GREENHOUSE_COMPANIES = [
    "cloudflare", "gitlab", "databricks", "mongodb", "elastic",
    "twilio", "stripe", "okta", "zscaler", "coinbase",
    "robinhood", "figma", "airbnb", "datadog", "newrelic",
    "razorpaysoftwareprivatelimited", "postman", "groww",
]

LEVER_COMPANIES = [
    "palantir", "plaid",
]

# --- 2. ADZUNA (broad job-board aggregator, good India coverage) ----------
# Free API — sign up at https://developer.adzuna.com/ to get app_id + app_key
ADZUNA_APP_ID = ""   # <-- fill in after signup
ADZUNA_APP_KEY = ""  # <-- fill in after signup
ADZUNA_COUNTRY = "in"  # India
ADZUNA_QUERIES = [
    "cloud engineer fresher",
    "cloud support associate",
    "cloud support engineer fresher",
    "AWS engineer entry level",
    "Azure engineer fresher",
    "cloud operations fresher",
    "cloud administrator fresher",
    "junior cloud engineer",
    "graduate engineer trainee cloud",
    "cybersecurity analyst fresher",
    "SOC analyst fresher",
    "security analyst entry level",
    "network security fresher",
    "information security fresher",
    "junior penetration tester",
    "DevOps engineer fresher",
    "junior devops engineer",
    "site reliability engineer fresher",
    "IT support engineer cloud fresher",
    "technical support engineer cloud",
    "systems administrator fresher",
    "network engineer fresher",
    "off campus drive cloud",
    "graduate engineer trainee IT",
]

# --- 3. FREE REMOTE JOB AGGREGATORS (no signup required) -------------------
# These cover globally-remote tech roles — useful since you're open to remote.
REMOTIVE_QUERIES = ["cloud", "devops", "aws", "cybersecurity", "security engineer"]

# --- 4. SKILL KEYWORDS ------------------------------------------------------
# Postings are scored on how many of these appear in the title/description.
# Grouped so the skills-trend page can show which cluster is hottest.
SKILL_KEYWORDS = {
    "cloud": [
        "aws", "azure", "gcp", "google cloud", "ec2", "s3", "lambda",
        "cloudformation", "terraform", "kubernetes", "docker", "iam",
        "vpc", "cloud engineer", "cloud support", "cloud administrator",
    ],
    "cybersecurity": [
        "security analyst", "soc analyst", "siem", "splunk", "cybersecurity",
        "cyber security", "information security", "infosec", "cyber",
        "penetration testing", "penetration tester", "pen testing", "vapt",
        "ethical hacking", "ceh", "vulnerability", "incident response",
        "security+", "network security", "endpoint security",
        "threat detection", "threat intelligence", "malware", "firewall",
        "cloud security", "security engineer", "security operations",
        "grc analyst", "iso 27001",
    ],
    "devops": [
        "ci/cd", "jenkins", "github actions", "ansible", "devops",
        "site reliability", "sre", "linux administration",
    ],
    "servicenow": [
        "servicenow", "itsm", "csa", "cad", "itom",
    ],
}

# --- 5. FRESHER / ENTRY-LEVEL DETECTION ------------------------------------
FRESHER_KEYWORDS = [
    "fresher", "entry level", "entry-level", "graduate", "0-1 year",
    "0-1 yrs", "0-2 years", "junior", "trainee", "associate engineer",
    "campus hire", "new grad",
]
# Postings mentioning any of these are EXCLUDED even if fresher words appear
SENIOR_EXCLUDE_KEYWORDS = [
    "senior", "sr.", "5+ years", "7+ years", "10+ years", "lead engineer",
    "principal", "staff engineer", "manager",
]

# --- 6. LOCATION PREFERENCE -------------------------------------------
# Jobs NOT matching any of these (in the location field OR description) are
# EXCLUDED entirely — not just ranked lower. Jobs matching are then ranked
# by their position in this list (remote first, then Hyderabad, etc).
LOCATION_PRIORITY = ["remote", "india", "hyderabad", "bangalore", "bengaluru"]

# A posting can say "remote" while actually meaning "remote, but only within
# the US/EU" — these phrases override a "remote" match and exclude the job,
# since it wouldn't actually be available to you.
LOCATION_EXCLUDE_KEYWORDS = [
    "us citizens only", "us-based candidates only", "united states only",
    "must be authorized to work in the united states", "must be based in the us",
    "eu residents only", "uk residents only", "remote - us", "remote (us)",
    "remote, us", "us remote only",
]

# --- 7. NOTIFICATION ---------------------------------------------------
# WhatsApp numbers to notify, in international format e.g. "91XXXXXXXXXX"
NOTIFY_NUMBERS = [
    # "91XXXXXXXXXX",
]

# Meta WhatsApp Cloud API credentials (set as GitHub Actions secrets, NOT here)
# WHATSAPP_TOKEN and WHATSAPP_PHONE_NUMBER_ID are read from environment variables
# in scripts/notify_whatsapp.py — see README for setup.
WHATSAPP_TEMPLATE_NAME = "job_alert"  # the approved template name you create in Meta Business Manager
