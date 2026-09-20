from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.verification_schema import VerificationParams, ResendVerificationLink
from app.services.verification_service import resend_lost_verification_link, verify_email

router = APIRouter()


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
