from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.dependencies.auth_dependency import get_current_user
from app.services.payment_service import start_payment

router = APIRouter()


@router.post("/{transaction_id}/")
def create_payment_route(
    transaction_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    start_payment(db=db, transaction_id=transaction_id, current_user=current_user)
