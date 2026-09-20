from fastapi import status
from sqlalchemy.orm import Session

from app.constants.verifications import TOKEN_EXPIRATION_TIME
from app.exceptions.app_exception import AppException
from app.enums.token_type import TokenType
from app.models.user_model import UserTable
from app.models.verification_token_model import VerificationTokenTable
from app.schemas.user_schema import CreateUser, AuthenticateUser, TokenResponse
from app.utils.error_codes import ErrorCode
from app.utils.jwt import generate_token
from app.utils.security import hash_password, verify_hash
from datetime import datetime, timedelta, timezone

from app.schemas.verification_schema import (
    VerificationEmailResponse,
    ResendVerificationLink,
)

from app.utils.emails import send_email
from app.utils.token import generate_raw_token, hash_raw_token


def create_user(data: CreateUser, db: Session) -> CreateUser:
    # Check if the email or the username already exist in the db
    existing_user = db.query(UserTable).filter(UserTable.email == data.email).first()

    # If exist throw an error
    if existing_user:
        raise AppException(
            message="Email address already exist, please log in",
            error_code=ErrorCode.EMAIL_TAKEN,
            status_code=status.HTTP_409_CONFLICT,
        )

    # If not hash the password
    hashed_password = hash_password(data.password)

    user_to_save = UserTable(
        email=data.email,
        surname=data.surname,
        name=data.name,
        hash_password=hashed_password,
    )

    # save the user in the db
    db.add(user_to_save)
    db.flush()
    send_verification_email(db=db, email=data.email, user_id=user_to_save.user_id)
    db.commit()
    db.refresh(user_to_save)

    return user_to_save


def authenticate_user(data: AuthenticateUser, db: Session) -> TokenResponse:

    existing_user = db.query(UserTable).filter(UserTable.email == data.email).first()

    if not existing_user:
        raise AppException(
            message="Email or password is incorrect, please verify",
            error_code=ErrorCode.AUTH_INVALID_CREDENTIALS,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    # check if the password matches
    password_is_match = verify_hash(existing_user.hash_password, data.password)

    # if password do not match -> raise http exception
    if not password_is_match:
        raise AppException(
            message="Email or password is incorrect, please verify",
            error_code=ErrorCode.AUTH_INVALID_CREDENTIALS,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    payload = {"user_id": existing_user.user_id}

    access_token = generate_token(payload=payload, token_type="access_token")

    # if password match -> generate a token
    return TokenResponse(access_token=access_token)


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
    url = f"http://127.0.0.1:8000/auth/verify-email?token={raw_token}"
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
