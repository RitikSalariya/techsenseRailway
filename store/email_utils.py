# store/email_utils.py
import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def send_app_email(to_email: str, subject: str, text_body: str) -> bool:
    """
    Send an email using Django's configured EMAIL_* settings (Gmail in production).
    """
    try:
        send_mail(
            subject=subject,
            message=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
        return True
    except Exception:
        logger.exception("Email send failed")
        return False
