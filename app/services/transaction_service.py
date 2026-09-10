import math
from decimal import Decimal

from fastapi import status
from sqlalchemy.orm import Session

from app.enums.pricing_unit import PricingUnit
from app.enums.product_status import ProductStatus
from app.enums.product_type import ProductType
from app.enums.transaction_status import TransactionStatus
from app.exceptions.app_exception import AppException
from app.models.product_model import ProductTable
from app.models.transaction_model import TransactionTable
from app.schemas.transaction_schema import CreateTransaction, TransactionResponse
from app.schemas.user_schema import CurrentUser
from app.utils.error_codes import ErrorCode


def create_transaction(
    product_id: int,
    data: CreateTransaction,
    db: Session,
    current_user: CurrentUser,
):
    product = (
        db.query(ProductTable)
        .where(
            ProductTable.product_id == product_id,
            ProductTable.product_status == ProductStatus.ACTIVE,
        )
        .first()
    )

    if product is None:
        raise AppException(
            message=f"Cannot create transaction. Product of id {product_id} does not exist or is Inactive",
            error_code=ErrorCode.PRODUCT_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    is_customer_product_owner = product.user_id == current_user.user_id
    if is_customer_product_owner:
        raise AppException(
            message=f"Cannot create transaction of your own product",
            error_code=ErrorCode.BAD_REQUEST,
            status_code=status.HTTP_403_FORBIDDEN,
        )

    message = ""

    if product.product_type == ProductType.SELL:

        t = (
            db.query(TransactionTable)
            .where(
                TransactionTable.product_id == product_id,
                TransactionTable.status.in_(
                    [
                        TransactionStatus.PENDING,
                        TransactionStatus.IN_PROGRESS,
                        TransactionStatus.COMPLETED,
                    ]
                ),
            )
            .first()
        )

        if t:
            raise AppException(
                message=f"Product is no longer available",
                error_code=ErrorCode.BAD_REQUEST,
                status_code=status.HTTP_403_FORBIDDEN,
            )

        message = f"You have bought {product.product_name}"
        transaction = TransactionTable(
            product_id=product_id,
            provider_id=product.user_id,
            customer_id=current_user.user_id,
            status=TransactionStatus.PENDING,
            amount=product.price,
        )
    elif product.product_type == ProductType.RENT:
        if data.scheduled_end is None or data.scheduled_start is None:
            raise AppException(
                message="Please provide starting date and end date",
                error_code=ErrorCode.MISSING_START_OR_END_DATE,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if data.scheduled_start >= data.scheduled_end:
            raise AppException(
                message="Start date cannot be after end date",
                error_code=ErrorCode.START_DATE_GREATER_THAN_END_DATE,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        transactions = (
            db.query(
                TransactionTable.scheduled_start_date,
                TransactionTable.scheduled_end_date,
                TransactionTable.status,
            )
            .where(
                TransactionTable.product_id == product_id,
            )
            .all()
        )
        # print(transactions)
        # input(type(transactions[0]))
        for transaction in transactions:
            if (
                transaction.scheduled_end_date > data.scheduled_start
                and transaction.scheduled_start_date < data.scheduled_end
            ) and (transaction.status != TransactionStatus.REJECTED):
                raise AppException(
                    message=f"This product wont be available between {data.scheduled_start} and {data.scheduled_end}",
                    error_code=ErrorCode.PRODUCT_ALREADY_RENTED,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        rental_duration = 0

        if product.pricing_unit == PricingUnit.HOUR:
            delta_time = data.scheduled_end - data.scheduled_start
            rental_duration = delta_time.total_seconds() / 3600
        elif product.pricing_unit == PricingUnit.DAY:
            delta_time = data.scheduled_end.date() - data.scheduled_start.date()
            rental_duration = int(delta_time.days)
        elif product.pricing_unit == PricingUnit.WEEK:
            number_of_weeks = math.ceil(
                int((data.scheduled_end.date() - data.scheduled_start.date()).days) / 7
            )

            rental_duration = int(number_of_weeks)

        total_price = Decimal(rental_duration) * Decimal(product.price)
        message = f"You have rented {product.product_name}"
        transaction = TransactionTable(
            product_id=product_id,
            provider_id=product.user_id,
            customer_id=current_user.user_id,
            status=TransactionStatus.PENDING,
            amount=total_price,
            scheduled_start_date=data.scheduled_start,
            scheduled_end_date=data.scheduled_end
        )

    elif product.product_type == ProductType.SERVICE:
        ...

    else:
        raise AppException(
            message=f"{product.product_type} does not exist.",
            error_code=ErrorCode.BAD_REQUEST,
            status_code=status.HTTP_403_FORBIDDEN,
        )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return TransactionResponse(message=message)
