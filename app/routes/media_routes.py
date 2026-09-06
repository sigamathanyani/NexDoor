from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.dependencies.auth_dependency import get_current_user
from app.dependencies.aws_dependency import get_s3_client
from app.schemas.product_media_schema import (
    ProductMediaResponse,
    RequestPresignedUrlData,
    S3MediaObjectResponse,
    CreateProductMediaObject,
)
from app.schemas.user_schema import CurrentUser
from app.services.media_service import get_presigned_url, get_presigned_url_for_creation, save_s3_media

router = APIRouter()


@router.post(
    "/get-presigned-url/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=S3MediaObjectResponse,
)
def get_presigned_url_for_upload_route(
    product_id: int,
    data: RequestPresignedUrlData,
    current_user=Depends(get_current_user),
    s3_client=Depends(get_s3_client),
    db: Session = Depends(get_db),
):
    return get_presigned_url(
        db,
        product_id,
        # data,
        current_user,
        s3_client,
        client_method='put_object'
    )

@router.post(
    "/get-presigned-url-for-creation/",
    status_code=status.HTTP_200_OK,
    response_model=S3MediaObjectResponse,
)
def get_presigned_url_for_upload_for_creation_route(
    s3_client=Depends(get_s3_client),
):
    return get_presigned_url_for_creation(
        s3_client,
        client_method='put_object'
    )

@router.get(
    "/get-product-media-url/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=S3MediaObjectResponse,
)
def get_presigned_url_for_getting_route(
    product_id: int,
    current_user=Depends(get_current_user),
    s3_client=Depends(get_s3_client),
    db: Session = Depends(get_db),
):
    return get_presigned_url(
        db,
        product_id,
        current_user,
        s3_client,
        client_method='get_object'
    )


@router.post(
    "/{product_id}/save-media",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductMediaResponse
)
def save_s3_media_route(
    data: CreateProductMediaObject,
    product_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    s3_client=Depends(get_s3_client),
):
    return save_s3_media(
        product_id=product_id, data=data, db=db, current_user=current_user, s3_client=s3_client
    )
