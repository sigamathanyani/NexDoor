from fastapi import status

from sqlalchemy.orm import Session

from app.enums.transaction_status import TransactionStatus
from app.enums.payment_status import PaymentStatus
from app.exceptions.app_exception import AppException
from app.models.payment_model import PaymentTable
from app.models.transaction_model import TransactionTable
from app.schemas.user_schema import CurrentUser
from app.utils.error_codes import ErrorCode


def start_payment(db: Session, transaction_id: int, current_user: CurrentUser):
    transaction = (
        db.query(TransactionTable)
        .where(
            TransactionTable.transaction_id == transaction_id,
            TransactionTable.customer_id == current_user.user_id,
            TransactionTable.status == TransactionStatus.ACCEPTED,
        )
        .first()
    )

    if transaction is None:
        raise AppException(
            message=f"Transaction of id {transaction_id} is not found",
            error_code=ErrorCode.TRANSACTION_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    payment = (
        db.query(PaymentTable)
        .where(
            PaymentTable.transaction_id == transaction_id,
            PaymentTable.payment_status == PaymentStatus.PAID,
        )
        .first()
    )

    if payment is not None:
        raise AppException(
            message=f"This transaction is already paid on the {payment.created_at}",
            error_code=ErrorCode.TRANSACTION_ALREADY_PAID,
            status_code=status.HTTP_403_FORBIDDEN,
        )

    ### ARE WE CALLING THE THIRD PARTY HERE ? PAYMENT GATEAWAY

    payment = PaymentTable(
        transaction_id=transaction_id,
        amount=transaction.amount,
    )

    db.add(payment)
    return
