import hashlib
import hmac

from passlib.context import CryptContext

from app.config import settings

pwd_ctx = CryptContext(
    schemes=["bcrypt"], deprecated="auto", bcrypt__truncate_error=False
)


def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)


def verify_hash(hash_password, plain_password):
    return pwd_ctx.verify(plain_password, hash_password)

def verify_payment_signature(paystack_signature, msg, ):
    expected_signature = hmac.new(
            key=settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
            msg=msg,
            digestmod=hashlib.sha512
        ).hexdigest()
    
    return paystack_signature == expected_signature