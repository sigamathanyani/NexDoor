from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.dependencies.auth_dependency import get_current_user
from app.dependencies.aws_dependency import get_s3_client
from app.schemas.product_media_schema import (
    RequestPresignedUrlData,
    S3MediaObjectResponse,
    CreateProductMediaObject,
)
from app.schemas.user_schema import CurrentUser
from app.services.media_service import get_presigned_url, save_s3_media

router = APIRouter()


@router.post(
    "/get-presigned-url",
    status_code=status.HTTP_200_OK,
    response_model=S3MediaObjectResponse,
)
def get_presigned_url_route(
    data: RequestPresignedUrlData,
    current_user=Depends(get_current_user),
    s3_client=Depends(get_s3_client),
    db: Session = Depends(get_db),
):
    return get_presigned_url(
        db,
        data,
        current_user,
        s3_client,
    )


@router.post(
    "save-media",
    status_code=status.HTTP_201_CREATED,
)
def save_s3_media_route(
    data: CreateProductMediaObject,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    s3_client=Depends(get_s3_client),
):
    return save_s3_media_route(
        data=data, db=db, current_user=current_user, s3_client=s3_client
    )
