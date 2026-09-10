from enum import Enum

class TransactionStatus(Enum):
    PENDING = 'PENDING' # The customer just created the transaction and waitong fro provider
    REJECTED = 'REJECTED' # Provider rejected the transaction
    IN_PROGRESS = 'IN_PROGRESS' # The rental/service is currently happening
    COMPLETED = 'COMPLETED' # The transaction is finished (SOLD/RENTAL DONE/SERVICE DONE)