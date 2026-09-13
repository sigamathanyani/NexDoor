from decimal import Decimal

from app.database.db import Base

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Numeric,
    DateTime as SQLALchemyDateTime,
    func,
)
from sqlalchemy import Enum as SQLAlchemyEnum

from app.enums.payment_status import PaymentStatus


class PaymentTable(Base):
    __tablename__ = 'Payments'
    
    payment_id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(
        Integer, ForeignKey("Transactions.transaction_id"), nullable=False, index=True
    )
    amount = Column(name="amount", type_=Numeric(10, 2), nullable=False)
    payment_status = Column(
        name="status",
        type_=SQLAlchemyEnum(PaymentStatus),
        nullable=False,
        server_default=PaymentStatus.UNPAID.value,
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
        server_default=func.now(),
    )
