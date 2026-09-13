from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.dependencies.auth_dependency import get_current_user
from app.schemas.notification_schema import NotificationResponse
from app.services.notification_service import get_notification, get_notifications

router = APIRouter()

@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[NotificationResponse],
)
def get_notifications_route(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_notifications(db=db, current_user=current_user)

@router.patch(
    "/{notification_id}/read",
    status_code=status.HTTP_200_OK,
    response_model=NotificationResponse,
)
def get_notification_route(
    notification_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_notification(db=db, notification_id=notification_id, current_user=current_user)
