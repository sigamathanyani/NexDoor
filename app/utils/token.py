import secrets
import hashlib


def generate_raw_token():
    return secrets.token_urlsafe(32)


def hash_raw_token(raw_token: str):
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
