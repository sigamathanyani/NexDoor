from enum import Enum

class TransactionStatus(Enum):
    PENDING = 'PENDING' # The customer just created the transaction and waitong fro provider
    ACCEPTED = 'ACCEPTED' # The provider just accepted the transaction
    REJECTED = 'REJECTED' # Provider rejected the transaction
    AWAITING_START = 'AWAITING_START' # Waiting for the date of transaction to start
    IN_PROGRESS = 'IN_PROGRESS' # The rental/service is currently happening
    COMPLETED = 'COMPLETED' # The transaction is finished (SOLD/RENTAL DONE/SERVICE DONE)