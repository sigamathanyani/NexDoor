from fastapi import status
from sqlalchemy.orm import Session

from app.exceptions.app_exception import AppException
from app.models.user_model import UserTable
from app.schemas.user_schema import CreateUser, AuthenticateUser, TokenResponse
from app.utils.error_codes import ErrorCode
from app.utils.jwt import generate_token
from app.utils.security import hash_password, verify_hash


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
    db.commit()
    db.refresh(user_to_save)

    return user_to_save


def authenticate_user(data: AuthenticateUser, db: Session) -> TokenResponse:

    existing_user = db.query(UserTable).filter(UserTable.email == data.email).first()

    if not existing_user:
        raise AppException(
            message='Email or password is incorrect, please verify',
            error_code=ErrorCode.AUTH_INVALID_CREDENTIALS,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    # check if the password matches
    password_is_match = verify_hash(existing_user.hash_password, data.password)

    # if password do not match -> raise http exception
    if not password_is_match:
        raise AppException(
            message='Email or password is incorrect, please verify',
            error_code=ErrorCode.AUTH_INVALID_CREDENTIALS,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    payload = {"user_id": existing_user.user_id}

    access_token = generate_token(payload=payload, token_type="access_token")

    # if password match -> generate a token
    return TokenResponse(access_token=access_token)
