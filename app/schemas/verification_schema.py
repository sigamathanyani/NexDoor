from pydantic import BaseModel, EmailStr


class VerificationParams(BaseModel):
    model_config = {"extra": "allow"}

    token: str
    
class VerificationEmailResponse(BaseModel):
    message: str

class ResendVerificationLink(BaseModel):
    email: EmailStr

class ForgetPassword(BaseModel):
    email: EmailStr
    
class ForgetPasswordResponse(BaseModel):
    message: str