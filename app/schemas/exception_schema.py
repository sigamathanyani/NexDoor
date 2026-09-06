from pydantic import BaseModel

from app.utils.error_codes import ErrorCode


class ExceptionResponse(BaseModel):
    message: str
    error_code: ErrorCode
