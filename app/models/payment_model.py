
from app.database.db import Base

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Numeric,
    DateTime as SQLALchemyDateTime,
    String,
    func,
)
from sqlalchemy import Enum as SQLAlchemyEnum

from app.enums.payment_gateways import PaymentGateway
from app.enums.payment_status import PaymentStatus


class PaymentTable(Base):
    __tablename__ = "Payments"

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
    payment_gateway = Column(
        name="gateway",
        type_=SQLAlchemyEnum(PaymentGateway),
        nullable=False,
    )
    payment_ref = Column(
        name="payment_ref", type_=String(100), nullable=False, unique=True
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
