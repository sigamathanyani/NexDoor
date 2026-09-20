from pydantic import BaseModel


class PaystackResponse(BaseModel):
    link: str
    status_code: int
    
class PaymentResponse(BaseModel):
    message: str
    status_code: int