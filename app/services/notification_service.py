from fastapi import status

from sqlalchemy.orm import Session

from app.enums.notification_code import NotificationCode
from app.exceptions.app_exception import AppException
from app.models.notification_model import NotificationTable
from app.models.product_model import ProductTable
from app.models.transaction_model import TransactionTable
from app.models.user_model import UserTable
from app.schemas.notification_schema import NotificationResponse
from app.schemas.user_schema import CurrentUser
from app.utils.error_codes import ErrorCode


def create_notification(
    db: Session,
    transaction_id: int,
    recipient_user_id: int,
):
    notification = NotificationTable(
        recipient_user_id=recipient_user_id, transaction_id=transaction_id
    )

    db.add(notification)

    return


def get_notifications(
    db: Session,
    current_user: CurrentUser,
):
    notifications = (
        db.query(
            NotificationTable,
            TransactionTable,
            ProductTable,
            UserTable,
        )
        .join(
            TransactionTable,
            TransactionTable.transaction_id == NotificationTable.transaction_id,
        )
        .join(
            ProductTable,
            ProductTable.product_id == TransactionTable.product_id,
        )
        .join(
            UserTable,
            UserTable.user_id == TransactionTable.customer_id,
        )
        .where(
            NotificationTable.recipient_user_id == current_user.user_id,
        )
        .all()
    )

    return [
        NotificationResponse(
            notification_id=n.notification_id,
            code=NotificationCode.NEW_TRANSACTION,
            message=f"You have a new rental request for '{p.product_name}' from {u.name} {u.surname}. Total: R{t.amount}.",
            is_read=n.is_read,
        )
        for n, t, p, u in notifications
    ]


def get_notification(
    db: Session,
    notification_id: int,
    current_user: CurrentUser,
):
    notification = (
        db.query(
            NotificationTable,
            TransactionTable,
            ProductTable,
            UserTable,
        )
        .join(
            TransactionTable,
            TransactionTable.transaction_id == NotificationTable.transaction_id,
        )
        .join(
            ProductTable,
            ProductTable.product_id == TransactionTable.product_id,
        )
        .join(
            UserTable,
            UserTable.user_id == TransactionTable.customer_id,
        )
        .where(
            NotificationTable.recipient_user_id == current_user.user_id,
            NotificationTable.notification_id == notification_id,
        )
        .first()
    )

    if not notification:
        raise AppException(
            message=f"Notification of id {notification_id} is not found",
            error_code=ErrorCode.NOTIFICATION_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    n, t, p, u = notification

    n.is_read = True
    db.commit()
    db.refresh(n)

    return NotificationResponse(
        notification_id=n.notification_id,
        code=NotificationCode.NEW_TRANSACTION,
        message=f"You have a new rental request for '{p.product_name}' from {u.name} {u.surname}. Total: R{t.amount}.",
        is_read=n.is_read,
    )


