
from enum import Enum


class PaymentStatus(Enum):
    UNPAID: str = "UNPAID"
    PAID: str = "PAID"
    FAILED: str = "FAILED"
    REFUNDED: str = "REFUNDED"
