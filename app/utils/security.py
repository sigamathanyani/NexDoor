from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=['bcrypt'], deprecated='auto', bcrypt__truncate_error=False)

def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)

def verify_hash(hash_password, plain_password):
    return pwd_ctx.verify(plain_password, hash_password)