from pydantic import BaseModel, EmailStr, field_validator

from app.utils.validators import password_validator, string_validator


class CreateUser(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str

    @field_validator("password")
    def validate_password(password):
        validator = password_validator(password)
        if validator is not None:
            raise ValueError(validator)
        return password

    @field_validator("name")
    def validate_name(name):
        validator = string_validator(name, "name")
        if validator is not None:
            raise ValueError(validator)
        return name

    @field_validator("surname")
    def validate_surname(surname):
        validator = string_validator(surname, "surname")
        if validator is not None:
            raise ValueError(validator)
        return surname


class AuthenticateUser(BaseModel):
    email: EmailStr
    password: str


class CurrentUser(BaseModel):
    user_id: int
    name: str
    surname: str


class TokenResponse(BaseModel):
    access_token: str
