"""
Sends a WhatsApp message per new job using Meta's WhatsApp Cloud API.

SETUP REQUIRED (one-time, see README.md for full steps):
1. Create a Meta for Developers app + WhatsApp product.
2. Get a permanent access token and your Phone Number ID.
3. Create and get approval for a message TEMPLATE (business-initiated messages
   require an approved template — free-form text only works within a 24h
   customer-initiated session, which doesn't apply here).
4. Store WHATSAPP_TOKEN and WHATSAPP_PHONE_NUMBER_ID as GitHub Actions secrets.

Template suggestion (name it "job_alert" to match config.WHATSAPP_TEMPLATE_NAME):
  Body: "New {{1}} role at {{2}}: {{3}}. Location: {{4}}. Apply: {{5}}"
  Variables filled at send time: skill_group, company, title, location, url
"""
import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

GRAPH_API_VERSION = "v20.0"


def _send_one(job, to_number, token, phone_number_id):
    skill_group = ", ".join(job.get("matched_skills", {}).keys()) or "Tech"
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{phone_number_id}/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": config.WHATSAPP_TEMPLATE_NAME,
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": skill_group},
                        {"type": "text", "text": job.get("company", "")},
                        {"type": "text", "text": job.get("title", "")[:60]},
                        {"type": "text", "text": job.get("location", "N/A")},
                        {"type": "text", "text": job.get("url", "")},
                    ],
                }
            ],
        },
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=15)
    if resp.status_code >= 300:
        print(f"WhatsApp send failed for {to_number}: {resp.status_code} {resp.text}")
    return resp.status_code < 300


def notify_all(new_jobs):
    token = os.environ.get("WHATSAPP_TOKEN")
    phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
    if not token or not phone_number_id:
        print("WHATSAPP_TOKEN / WHATSAPP_PHONE_NUMBER_ID not set — skipping notifications.")
        return
    if not config.NOTIFY_NUMBERS:
        print("No numbers configured in config.NOTIFY_NUMBERS — skipping notifications.")
        return

    for job in new_jobs:
        for number in config.NOTIFY_NUMBERS:
            _send_one(job, number, token, phone_number_id)
