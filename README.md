# Elite Entrepreneurs Website

Static HTML/CSS/JS site with a small Flask backend for the guest visit form.

## Files

- `index.html` — the entire site (single page, no build step)
- `Headshots/`, `illustrations/`, `logo/` — images
- `server.py` — serves the site and handles the form (reCAPTCHA + Brevo email)
- `requirements.txt` — Python dependencies (`flask`, `requests`)

## Setup (when ready to go live)

### 1. reCAPTCHA
1. Go to the [Google reCAPTCHA admin console](https://www.google.com/recaptcha/admin) and register a new **reCAPTCHA v2 ("I'm not a robot" checkbox)** site.
2. Add `eliteentrepreneurs.biz` and your Replit dev domain to the allowed domains.
3. In `index.html`, replace `RECAPTCHA_SITE_KEY_HERE` with the **site key**.
4. Save the **secret key** for step 3 below.

### 2. Brevo
1. Create a free [Brevo](https://www.brevo.com) account.
2. Verify a sender address (e.g. `no-reply@eliteentrepreneurs.biz`).
3. Create an API key under **SMTP & API → API Keys**.

### 3. Replit Secrets
Set these in the Replit **Secrets** tool (never in code):

| Key | Value |
|---|---|
| `RECAPTCHA_SECRET_KEY` | from step 1 |
| `BREVO_API_KEY` | from step 2 |
| `SENDER_EMAIL` | your Brevo-verified sender |
| `TO_EMAIL` | inbox that receives guest requests |

### 4. Run
```
pip install -r requirements.txt
python server.py
```
Site serves on port 3000. On Replit, set the run command to `python server.py`.

## Notes

- Until the secrets are set, the form shows a friendly error and points guests to Facebook. The rest of the site works as pure static HTML.
- If you preview the site statically (e.g. GitHub Pages), the form cannot submit — the backend only runs on Replit.
