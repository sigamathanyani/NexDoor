from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.dependencies.auth_dependency import get_current_user
from app.schemas.transaction_schema import TransactionResponse
from app.schemas.user_schema import CurrentUser
from app.services.transaction_service import create_transaction

router = APIRouter()


@router.post(
    "/create-transaction/{product_id}",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction_route(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return create_transaction(product_id=product_id, db=db, current_user=current_user)
