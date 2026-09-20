from datetime import datetime, timedelta, timezone

from fastapi import status

from sqlalchemy.orm import Session

from app.constants.verifications import TOKEN_EXPIRATION_TIME
from app.enums.token_type import TokenType
from app.exceptions.app_exception import AppException
from app.models.user_model import UserTable
from app.models.verification_token_model import VerificationTokenTable
from app.schemas.verification_schema import (
    VerificationEmailResponse,
    ResendVerificationLink,
)
from app.utils.emails import send_email
from app.utils.error_codes import ErrorCode
from app.utils.token import generate_raw_token, hash_raw_token


def _send_verification_email(
    db: Session,
    email: str,
    user_id: int,
):
    raw_token = generate_raw_token()
    hashed_raw_token = hash_raw_token(raw_token)

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    exp_time = now + timedelta(minutes=TOKEN_EXPIRATION_TIME)

    verification_token = VerificationTokenTable(
        user_id=user_id,
        token_hash=hashed_raw_token,
        token_type=TokenType.EMAIL_VERIFICATION,
        expires_at=exp_time,
    )
    url = f"http://127.0.0.1:8000/verification/verify-email?token={raw_token}"
    db.add(verification_token)
    send_email(to=email, url_link=url)


def send_verification_email(
    db: Session,
    email: str,
    user_id: int,
):
    _send_verification_email(
        db=db,
        email=email,
        user_id=user_id,
    )

    return VerificationEmailResponse(message="Check your email for verification link")


def verify_email(db: Session, query_params):
    raw_token = query_params.token

    hashed_raw_token = hash_raw_token(raw_token)

    db_token_data = (
        db.query(VerificationTokenTable)
        .where(VerificationTokenTable.token_hash == hashed_raw_token)
        .first()
    )

    if db_token_data is None:
        raise AppException(
            message="Something is wrong with the link you provided",
            error_code=ErrorCode.LINK_BROKEN,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if db_token_data.token_type != TokenType.EMAIL_VERIFICATION:
        raise AppException(
            message="This is an invalid email verification link",
            error_code=ErrorCode.LINK_BROKEN,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    token_expired = (
        datetime.now(tz=timezone.utc).replace(tzinfo=None) > db_token_data.expires_at
    )
    if token_expired:
        raise AppException(
            message="The link to verify has already expire please request a new one",
            error_code=ErrorCode.VERIFICATION_TOKEN_EXPIRED,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    u = db.query(UserTable).where(UserTable.user_id == db_token_data.user_id).first()

    if u is None:
        raise AppException(
            message="User not found of this token",
            error_code=ErrorCode.USER_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if u.is_verified:
        return VerificationEmailResponse(message="This account is already verified")
    u.is_verified = True
    db.delete(db_token_data)
    db.commit()
    db.refresh(u)

    return VerificationEmailResponse(message="Your account is now verified")


def resend_lost_verification_link(data: ResendVerificationLink, db: Session):
    u = db.query(UserTable).where(UserTable.email == data.email).first()
    if u is None:
        raise AppException(
            message="User not found of this email",
            error_code=ErrorCode.USER_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if u.is_verified:
        return VerificationEmailResponse(message="This account is already verified")

    verification = (
        db.query(VerificationTokenTable)
        .where(
            VerificationTokenTable.user_id == u.user_id,
            VerificationTokenTable.token_type == TokenType.EMAIL_VERIFICATION,
        )
        .first()
    )

    if verification is None:
        _send_verification_email(db=db, email=data.email, user_id=u.user_id)
    else:
        raw_token = generate_raw_token()
        hashed_raw_token = hash_raw_token(raw_token)

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        exp_time = now + timedelta(minutes=TOKEN_EXPIRATION_TIME)
        verification.token_hash = hashed_raw_token
        verification.expires_at = exp_time

        url = f"http://127.0.0.1:8000/verification/verify-email?token={raw_token}"
        send_email(to=data.email, url_link=url)

    db.commit()
    return VerificationEmailResponse(message="Check your email for verification link")
