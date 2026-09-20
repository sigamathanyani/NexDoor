from typing_extensions import Annotated

from fastapi import APIRouter, Query
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.user_schema import CreateUser, AuthenticateUser, CurrentUser
from app.schemas.verification_schema import ResendVerificationLink, VerificationParams
from app.services.auth_service import create_user, authenticate_user, resend_lost_verification_link, verify_email
from app.dependencies.auth_dependency import get_current_user

router = APIRouter()


@router.post("/register")
def register_user(user_data: CreateUser, db: Session = Depends(get_db)):
    return create_user(user_data, db=db)


@router.post("/login")
def login_user(user_data: AuthenticateUser, db: Session = Depends(get_db)):
    return authenticate_user(user_data, db=db)


@router.get("/me")
def read_current_user(current_user: CurrentUser = Depends(get_current_user)):
    return current_user

@router.get("/verify-email")
def verify_email_route(
    query_params: Annotated[VerificationParams, Query()], db: Session = Depends(get_db)
):
    return verify_email(
        db=db,
        query_params=query_params,
    )

@router.post("/resend-verification-email")
def resend_email_verification_route(
    data: ResendVerificationLink, db: Session = Depends(get_db)
):
    return resend_lost_verification_link(
        data=data,
        db=db,
    )
