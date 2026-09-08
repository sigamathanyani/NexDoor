from fastapi import status
from sqlalchemy.orm import Session

from app.enums.product_status import ProductStatus
from app.enums.product_type import ProductType
from app.enums.transaction_status import TransactionStatus
from app.exceptions.app_exception import AppException
from app.models.product_model import ProductTable
from app.models.transaction_model import TransactionTable
from app.schemas.transaction_schema import TransactionResponse
from app.schemas.user_schema import CurrentUser
from app.utils.error_codes import ErrorCode


def create_transaction(
    product_id: int,
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
