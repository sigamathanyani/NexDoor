from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.dependencies.auth_dependency import get_current_user
from app.schemas.paystack_schema import PaystackResponse, PaymentResponse
from app.services.payment_service import paying, start_payment

router = APIRouter()


@router.post(
    "/webhook/",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
)
async def paying_route(
    request: Request,
    db: Session = Depends(get_db),
    webhook_signature: str = Header(None, alias="x-paystack-signature"),
):
    return await paying(db=db, request=request, webhook_signature=webhook_signature)


@router.post(
    "/{transaction_id}/",
    response_model=PaystackResponse,
    status_code=status.HTTP_200_OK,
)
def create_payment_route(
    transaction_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return start_payment(
        db=db, transaction_id=transaction_id, current_user=current_user
    )
