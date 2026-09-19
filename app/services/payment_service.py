import json

from fastapi import status, Request
import uuid

from sqlalchemy.orm import Session

from app.config import settings
from app.enums.currencies import Currency
from app.enums.payment_gateways import PaymentGateway
from app.enums.product_type import ProductType
from app.enums.transaction_status import TransactionStatus
from app.enums.payment_status import PaymentStatus
from app.exceptions.app_exception import AppException
from app.integrations.paystack.client import initialize_transaction
from app.models.payment_model import PaymentTable
from app.models.product_model import ProductTable
from app.models.transaction_model import TransactionTable
from app.schemas.paystack_schema import PaymentResponse, PaystackResponse
from app.schemas.user_schema import CurrentUser
from app.utils.error_codes import ErrorCode
from app.utils.security import verify_payment_signature


def start_payment(db: Session, transaction_id: int, current_user: CurrentUser):
    transaction = (
        db.query(TransactionTable)
        .where(
            TransactionTable.transaction_id == transaction_id,
            TransactionTable.customer_id == current_user.user_id,
        )
        .first()
    )

    if transaction is None:
        raise AppException(
            message=f"Transaction of id {transaction_id} is not found.",
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

    amount_in_cents = int(transaction.amount * 100)
    transaction_ref = f"{transaction.transaction_id}-{uuid.uuid4()}"

    paystack_res = initialize_transaction(
        email="thanyaniinnocent20@gmail.com",
        amount=amount_in_cents,
        currency=Currency.RANDS.value,
        reference=transaction_ref,
    )

    paystack_res_dict = json.loads(paystack_res.text)

    if paystack_res.status_code != status.HTTP_200_OK:
        raise AppException(
            message=paystack_res_dict["message"],
            status_code=paystack_res.status_code,
            error_code=ErrorCode.PAYSTACK_ERROR,
        )
    payment = PaymentTable(
        transaction_id=transaction_id,
        amount=transaction.amount,
        payment_status=PaymentStatus.UNPAID,
        payment_ref=paystack_res_dict["data"]["reference"],
        payment_gateway=PaymentGateway.PAYSTACK.value,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)
    return PaystackResponse(
        link=paystack_res_dict["data"]["authorization_url"],
        status_code=paystack_res.status_code,
    )


async def paying(db: Session, request: Request, webhook_signature: str):
    body = await request.body()
    is_verified = verify_payment_signature(webhook_signature, body)

    if not is_verified:
        raise AppException(
            message="Invalid payment signature",
            error_code=ErrorCode.INVALID_PAYMENT_SIGNATURE,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    body_dict = json.loads(body)
    event = body_dict["event"]
    pay_status = body_dict["data"]["status"]
    gateway_response = body_dict["data"]["gateway_response"]
    gateway_response_code = body_dict["data"]["gateway_response_code"]
    reference = body_dict["data"]["reference"]

    if (
        event == "charge.success"
        and pay_status == "success"
        and gateway_response == "Successful"
        and gateway_response_code == "approved"
    ):
        payment = (
            db.query(PaymentTable).where(PaymentTable.payment_ref == reference).first()
        )

        if payment is None:
            raise AppException(
                message="Payment of this reference does not exist",
                error_code=ErrorCode.PAYMENT_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if payment.payment_status == PaymentStatus.PAID:
            return

        transaction, product = (
            db.query(TransactionTable, ProductTable)
            .join(ProductTable, TransactionTable.product_id == ProductTable.product_id)
            .where(TransactionTable.transaction_id == payment.transaction_id)
            .first()
        )

        if transaction is None or product is None:
            raise AppException(
                message="Transaction or product is not found",
                error_code=ErrorCode.PRODUCT_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if product.product_type == ProductType.SELL:
            transaction.status = TransactionStatus.IN_PROGRESS
        else:
            transaction.status = TransactionStatus.AWAITING_START

        payment.payment_status = PaymentStatus.PAID
        db.add(payment)
        db.add(transaction)

        db.commit()
        db.refresh(payment)
        db.refresh(transaction)

    return PaymentResponse(
        message=gateway_response_code, status_code=status.HTTP_200_OK
    )
