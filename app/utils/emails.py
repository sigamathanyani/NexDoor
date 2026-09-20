import resend

from app.config import settings


def send_email(to: str, url_link: str, html: str = ''):
    resend.api_key = settings.RESEND_EMAIL_API_KEY

    r = resend.Emails.send(
        {
            "from": "onboarding@resend.dev",
            "to": to,
            "subject": "Please verify your email",
            "html": f"<p>Verify email {url_link}</p>",
        }
    )
