from pydantic import BaseModel, EmailStr, field_validator

from app.utils.validators import password_validator


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
    
class NewPassword(BaseModel):
    new_password: str
    
    @field_validator("new_password")
    def validate_password(new_password):
        validator = password_validator(new_password)
        if validator is not None:
            raise ValueError(validator)
        return new_password
