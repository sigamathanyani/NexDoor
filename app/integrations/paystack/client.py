import httpx
from app.config import settings


def initialize_transaction(email, amount, currency, reference):
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "email": email,
        "amount": amount,
        "currency": currency,
        "reference": reference,
    }

    return httpx.post(
        settings.PAYSTACK_URL, headers=headers, json=body
    )
