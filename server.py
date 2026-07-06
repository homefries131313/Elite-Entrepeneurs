"""Elite Entrepreneurs — static site server + guest visit form endpoint.

Serves the static site and handles POST /api/visit-request:
verifies Google reCAPTCHA, then emails the submission via Brevo.

Required environment variables (set these in Replit Secrets):
  RECAPTCHA_SECRET_KEY  - from Google reCAPTCHA admin console
  BREVO_API_KEY         - from Brevo (SMTP & API > API Keys)
  SENDER_EMAIL          - a Brevo-verified sender address
  TO_EMAIL              - where guest requests are delivered
                          (defaults to no-reply@eliteentrepreneurs.biz)
"""

import html
import os

import requests
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder=".", static_url_path="")

REQUIRED_FIELDS = ["name", "email", "business", "profession"]
OPTIONAL_FIELDS = ["citystate", "heard", "member", "notes"]
FIELD_LABELS = {
    "name": "Full name",
    "email": "Email",
    "business": "Business name",
    "profession": "What they do",
    "citystate": "City & state",
    "heard": "How they heard about us",
    "member": "Invited by member",
    "notes": "Notes",
}


@app.get("/")
def home():
    return send_from_directory(".", "index.html")


@app.post("/api/visit-request")
def visit_request():
    data = request.get_json(force=True, silent=True) or {}

    missing = [f for f in REQUIRED_FIELDS if not str(data.get(f, "")).strip()]
    if missing:
        return jsonify(ok=False, error=f"Missing required fields: {', '.join(missing)}"), 400

    # --- reCAPTCHA verification ---
    secret = os.environ.get("RECAPTCHA_SECRET_KEY")
    if secret:
        token = data.get("recaptcha", "")
        if not token:
            return jsonify(ok=False, error="Please complete the reCAPTCHA."), 400
        check = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": secret, "response": token},
            timeout=10,
        ).json()
        if not check.get("success"):
            return jsonify(ok=False, error="reCAPTCHA verification failed."), 400
    else:
        app.logger.warning("RECAPTCHA_SECRET_KEY not set; skipping captcha verification.")

    # --- Send email via Brevo ---
    api_key = os.environ.get("BREVO_API_KEY")
    if not api_key:
        return jsonify(ok=False, error="Mailer is not configured yet."), 500

    rows = ""
    for field in REQUIRED_FIELDS + OPTIONAL_FIELDS:
        value = str(data.get(field, "")).strip()
        if value:
            rows += (
                f"<tr><td style='padding:6px 12px;font-weight:bold'>{FIELD_LABELS[field]}</td>"
                f"<td style='padding:6px 12px'>{html.escape(value)}</td></tr>"
            )

    payload = {
        "sender": {
            "name": "Elite Entrepreneurs Website",
            "email": os.environ.get("SENDER_EMAIL", "no-reply@eliteentrepreneurs.biz"),
        },
        "to": [{"email": os.environ.get("TO_EMAIL", "no-reply@eliteentrepreneurs.biz")}],
        "replyTo": {"email": str(data["email"]).strip()},
        "subject": f"Guest visit request: {str(data['name']).strip()}",
        "htmlContent": (
            "<h2>New guest visit request</h2>"
            f"<table style='border-collapse:collapse'>{rows}</table>"
            "<p>Reply to this email to reach the guest directly.</p>"
        ),
    }

    resp = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        json=payload,
        headers={"api-key": api_key, "content-type": "application/json"},
        timeout=10,
    )
    if resp.status_code not in (200, 201):
        app.logger.error("Brevo error %s: %s", resp.status_code, resp.text)
        return jsonify(ok=False, error="Could not send email."), 502

    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
