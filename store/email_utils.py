# store/email_utils.py
import os
import logging
import requests

logger = logging.getLogger(__name__)

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

def send_brevo_email(to_email: str, subject: str, text_body: str):
    """
    Send an email using Brevo HTTP API.
    If BREVO_API_KEY is not set, just log and fail gracefully.
    """
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("DEFAULT_FROM_EMAIL", "techsensetechnogiesltd@gmail.com")

    if not api_key:
        logger.error(
            "BREVO_API_KEY is not set. Falling back to NO-OP email send."
        )
        # Do NOT crash, just pretend it failed
        return False

    payload = {
        "sender": {"name": "Techsense", "email": sender_email},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": text_body,
    }

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
        "accept": "application/json",
    }

    try:
        resp = requests.post(BREVO_API_URL, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        return True
    except Exception:
        logger.exception("Brevo email send failed")
        return False
