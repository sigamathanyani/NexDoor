from datetime import datetime, timedelta

from fastapi import HTTPException, status
from jose import ExpiredSignatureError, JWTError, jwt

from app.utils.error_codes import ErrorCode


from app.config import settings


def generate_token(payload: dict, token_type: str):
    try:
        payload_copy = payload.copy()
        expire = datetime.now() + timedelta(minutes=10)

        payload_copy.update({'exp': expire, 'token_type': token_type})
    except ExpiredSignatureError as ex:
        raise
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    
    return jwt.encode(claims=payload_copy, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str):
    try:
        return jwt.decode(token=token, key=settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Token has expired please log in again",
                "error_code": ErrorCode.AUTH_TOKEN_EXPIRED
            }
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Invalid Token",
                "error_code": ErrorCode.AUTH_TOKEN_INVALID
            }
        )