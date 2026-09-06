from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Numeric,
    DateTime as SQLALchemyDateTime,
    func,
)

from sqlalchemy import Enum as SQLAlchemyEnum

from app.database.db import Base
from app.enums.transaction_status import TransactionStatus


class TransactionTable(Base):
    __tablename__ = "Transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(
        Integer, ForeignKey("Products.product_id"), nullable=False, index=True
    )
    provider_id = Column(
        Integer, ForeignKey("Users.user_id"), nullable=False, index=True
    )
    customer_id = Column(
        Integer, ForeignKey("Users.user_id"), nullable=False, index=True
    )
    status = Column(
        name="status",
        type_=SQLAlchemyEnum(TransactionStatus),
        nullable=False,
        server_default=TransactionStatus.PENDING.value,
    )
    amount = Column(name="total_amount", type_=Numeric(10, 2), nullable=False)
    scheduled_start_date = Column(
        name="scheduled_start", type_=SQLALchemyDateTime(timezone=True)
    )
    scheduled_end_date = Column(
        name="scheduled_end", type_=SQLALchemyDateTime(timezone=True)
    )
    created_at = Column(
        name="created_at",
        type_=SQLALchemyDateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        name="updated_at",
        type_=SQLALchemyDateTime(timezone=True),
        nullable=False,
        onupdate=func.now(),
    )
