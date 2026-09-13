from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    DateTime as SQLALchemyDateTime,
    func,
)

from app.database.db import Base


class NotificationTable(Base):
    __tablename__ = "Notifications"

    notification_id = Column(Integer, primary_key=True, index=True, nullable=False)
    recipient_user_id = Column(
        Integer, ForeignKey("Users.user_id"), nullable=False, index=True
    )
    transaction_id = Column(
        Integer, ForeignKey("Transactions.transaction_id"), nullable=False, index=True
    )
    is_read = Column(Boolean, nullable=False, server_default="0")
    created_at = Column(
        name="created_at",
        type_=SQLALchemyDateTime(
            timezone=True,
        ),
        nullable=False,
        server_default=func.now(),
    )
