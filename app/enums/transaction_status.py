from enum import Enum

class TransactionStatus(Enum):
    PENDING = 'PENDING'
    REJETCED = 'REJETCED'
    IN_PROGRESS = 'IN_PROGRESS'
    ACCEPTED = 'ACCEPTED'