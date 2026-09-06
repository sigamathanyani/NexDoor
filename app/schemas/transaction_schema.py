from datetime import datetime

from pydantic import BaseModel

class CreateTransaction(BaseModel):
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None