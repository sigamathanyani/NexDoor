from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.dependencies.auth_dependency import get_current_user
from app.schemas.transaction_schema import (
    AcceptTransactionResponse,
    CreateTransaction,
    RejectTransactionResponse,
    TransactionResponse,
)
from app.schemas.user_schema import CurrentUser
from app.services.transaction_service import accept_transaction, create_transaction, reject_transaction

router = APIRouter()


@router.post(
    "/create-transaction/{product_id}",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction_route(
    product_id: int,
    data: CreateTransaction,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return create_transaction(
        product_id=product_id, data=data, db=db, current_user=current_user
    )


@router.patch(
    "/{transaction_id}/accept",
    response_model=AcceptTransactionResponse,
    status_code=status.HTTP_200_OK,
)
def accept_transaction_route(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return accept_transaction(
        db=db, current_user=current_user, transaction_id=transaction_id
    )

@router.patch(
    "/{transaction_id}/reject",
    response_model=RejectTransactionResponse,
    status_code=status.HTTP_200_OK,
)
def reject_transaction_route(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return reject_transaction(
        db=db, current_user=current_user, transaction_id=transaction_id
    )
