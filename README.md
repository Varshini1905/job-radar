# Signal — Fresher Job Radar (Cloud & Cybersecurity)

Scans company job boards + Adzuna every 2 hours, filters for fresher-level
cloud/cybersecurity postings, WhatsApps you new matches, and publishes a
dashboard with the job feed, skill trends, and your learning tracker.

**Cost: $0.** Everything below uses free tiers (GitHub Actions free minutes,
GitHub Pages free hosting, Adzuna free API, Meta WhatsApp free tier for
low volume).

---

## Step 1 — Create the GitHub repo

1. Go to github.com → New repository → name it e.g. `job-radar` → Public (required for free GitHub Pages) or Private (works too, Pages needs GitHub Pro for private repos — so Public is simplest).
2. Upload every file from this project into the repo, keeping the folder structure exactly as-is (including the hidden `.github/workflows/scan.yml`).

If you're comfortable with git:
```bash
git init
git add .
git commit -m "Initial job radar setup"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/job-radar.git
git push -u origin main
```

## Step 2 — Get an Adzuna API key (free, 2 minutes)

1. Go to https://developer.adzuna.com/ → Sign up.
2. Copy your **App ID** and **App Key**.
3. Open `config.py` in the repo and paste them into `ADZUNA_APP_ID` and `ADZUNA_APP_KEY`.

This is what covers general Indian job boards for cloud/cybersecurity roles beyond the Greenhouse/Lever company list.

## Step 3 — Set up WhatsApp notifications (Meta Cloud API, free tier)

1. Go to https://developers.facebook.com/ → create an app → add the **WhatsApp** product.
2. In the WhatsApp setup screen, you'll get a **temporary access token** and a **Phone Number ID** immediately — good enough for testing.
3. For it to keep working long-term (temp tokens expire in 24h), generate a **permanent token**: Business Settings → System Users → create a system user → generate token with `whatsapp_business_messaging` permission.
4. Create a **message template** (required for us to message you first, since these are business-initiated, not replies):
   - Meta Business Manager → WhatsApp Manager → Message Templates → Create
   - Name it exactly `job_alert` (matches `config.WHATSAPP_TEMPLATE_NAME`)
   - Body: `New {{1}} role at {{2}}: {{3}}. Location: {{4}}. Apply: {{5}}`
   - Submit for approval — usually approved within a few hours.
5. Add your WhatsApp number(s) (the ones that should receive alerts) to `config.NOTIFY_NUMBERS` in international format, no `+`, e.g. `"919876543210"`.

## Step 4 — Add secrets to GitHub

In your repo: **Settings → Secrets and variables → Actions → New repository secret**

Add two secrets:
- `WHATSAPP_TOKEN` — your permanent access token from Step 3
- `WHATSAPP_PHONE_NUMBER_ID` — your Phone Number ID from Step 3

These are kept encrypted and never appear in code or logs.

## Step 5 — Turn on GitHub Pages (hosts your dashboard for free)

1. Repo → **Settings → Pages**
2. Source: **Deploy from a branch** → Branch: `main` → Folder: `/ (root)` → Save.
3. Your dashboard will be live at:
   `https://YOUR_USERNAME.github.io/job-radar/dashboard/`
   (takes 1-2 minutes to go live after first save)

## Step 6 — Turn on the scanner

The workflow in `.github/workflows/scan.yml` runs automatically every 2 hours
once it's in the repo — no extra step needed. To test it immediately instead
of waiting:

Repo → **Actions** tab → **Job Scanner** workflow → **Run workflow** button.

Check the run logs to confirm it fetched jobs and (if any matched) sent WhatsApp messages.

---

## Study Squad Setup (shared learning room with V, or anyone else)

This is optional — the Job Feed, Skill Trends, and your personal Learning
Tracker all work without it. But if you want a live-synced space where you
and V (or others) can each add resources, track certifications, and see
each other's additions in real time, it needs a small free database.

**Why Firebase:** the dashboard is a static site (no server of its own), so
two people in different places can't write to the same data without
something in the middle. Firebase's free tier ("Spark plan") handles this —
no credit card required, and at the scale of a couple of people tracking
study progress you will not come close to the free limits.

1. Go to https://console.firebase.google.com/ → **Add project** → name it
   anything (e.g. `study-squad`) → you can skip Google Analytics, not needed.
2. Once created, click the **Web** icon (`</>`) to register a web app →
   name it anything → **do not** check "set up Firebase Hosting" (you're
   already using GitHub Pages).
3. Firebase will show you a config object like this:
   ```js
   const firebaseConfig = {
     apiKey: "AIzaSy...",
     authDomain: "study-squad-xxxx.firebaseapp.com",
     projectId: "study-squad-xxxx",
     storageBucket: "study-squad-xxxx.appspot.com",
     messagingSenderId: "123456789",
     appId: "1:123456789:web:abcdef123456"
   };
   ```
   Copy the whole thing and paste it into `dashboard/firebase-config.js` in
   the repo, replacing the placeholder values.
4. In the Firebase console, go to **Build → Firestore Database** → **Create database** →
   choose a location close to you (e.g. `asia-south1` for India) → start in
   **test mode** for now (this allows open read/write — fine for a private
   two-person project, but see the security note below).
5. Commit and push `firebase-config.js` to GitHub, wait for Pages to
   redeploy (~1-2 min), then open your dashboard's **Study Squad** tab —
   it should now be live instead of showing the setup notice.
6. Add yourself as a member (type your name → "Add me"), then send V the
   dashboard URL — when V adds their own name and starts adding resources,
   you'll both see everything update on refresh (Firestore syncs live, so
   often you won't even need to refresh).

**Security note:** "test mode" Firestore rules allow anyone with your config
to read/write the database — fine for a low-stakes shared study tracker
between friends, but don't put anything sensitive in it. If you want it
locked down further later, Firebase's console lets you restrict rules to
specific fields/collections without code changes — ask me if you want help
tightening this once it's running.



- **Add companies**: edit `GREENHOUSE_COMPANIES` / `LEVER_COMPANIES` in `config.py`. Find a company's slug from their careers page URL (`boards.greenhouse.io/SLUG` or `jobs.lever.co/SLUG`).
- **Add/change skill keywords**: edit `SKILL_KEYWORDS` in `config.py`.
- **Change scan frequency**: edit the `cron` line in `.github/workflows/scan.yml` (currently every 2 hours — cron syntax: minute hour day month weekday).
- **Update learning progress**: edit `data/learning_tracker.json` directly — change `status` and `percent` per topic, commit, and the dashboard reflects it immediately.

## How the pieces fit together

```
GitHub Actions (every 2h)
   → fetch_jobs.py   (pulls from Greenhouse, Lever, Adzuna)
   → filter_jobs.py  (fresher check + skill match + location rank)
   → dedupe.py        (skips jobs already notified)
   → notify_whatsapp.py (sends WhatsApp template message for new matches)
   → writes data/jobs.json + data/skills_trends.json
   → commits data/ back to the repo
        ↓
GitHub Pages serves dashboard/index.html, which reads those JSON files
```

## Known limitations (be aware)

- LinkedIn, Naukri, and Indeed are **not** scraped directly — their terms of
  service block automated scraping and it's fragile/risky. Adzuna covers a
  good chunk of Indian listings instead. You can still manually check those
  three periodically.
- Adzuna's free tier has a request cap (generous for this use case, but if
  you add many more query terms you may hit it — check your dashboard on
  developer.adzuna.com if scans start failing).
- Greenhouse/Lever company list is a starting set — most are global/product
  companies, not India-specific. Add more slugs as you find companies you like.
- **Large enterprises (AMD, NVIDIA, Intel, Oracle, Red Hat, HashiCorp, etc.)
  typically don't use Greenhouse or Lever** — they run on Workday, SAP
  SuccessFactors, or custom ATS platforms that don't offer a simple public
  JSON API the way Greenhouse/Lever do. This scanner currently only supports
  Greenhouse + Lever + Adzuna. Adding Workday support is possible (many
  Workday career sites do have a semi-public JSON endpoint, just messier and
  less standardized company-to-company) — worth doing as a future addition
  if you find you're missing a specific company you really want covered.
