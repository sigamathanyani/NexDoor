from datetime import datetime

from pydantic import BaseModel

class CreateTransaction(BaseModel):
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    
class TransactionResponse(BaseModel):
    message: str


class AcceptTransactionResponse(BaseModel):
    message: str
    transaction_id: int

class RejectTransactionResponse(BaseModel):
    message: str
    transaction_id: int