from pydantic import BaseModel

from app.enums.notification_code import NotificationCode


class NotificationResponse(BaseModel):
    notification_id: int
    code: NotificationCode
    message: str
    is_read: bool
