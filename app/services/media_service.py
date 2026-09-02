import uuid

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.config import settings

from app.models.media_model import ProductMediaTable
from app.models.product_model import ProductTable
from app.schemas.product_media_schema import (
    RequestPresignedUrlData,
    S3MediaObjectResponse,
    CreateProductMediaObject,
)
from app.schemas.user_schema import CurrentUser

from botocore.exceptions import ClientError


def get_presigned_url(
    db: Session,
    data: RequestPresignedUrlData,
    current_user: CurrentUser,
    s3_client,
    client_method="put_object",
):
    product = (
        db.query(ProductTable)
        .filter(
            and_(
                ProductTable.product_id == data.product_id,
                ProductTable.user_id == current_user.user_id,
            )
        )
        .first()
    )

    if not product:
        return None

    product_media_count = (
        db.query(ProductMediaTable)
        .filter(ProductMediaTable.product_id == data.product_id)
        .count()
    )

    if product_media_count >= 5:
        return None

    extension = data.content_type.split("/")[1]
    file_id = str(uuid.uuid4())
    file_unique_name = f"products/{data.product_id}/{file_id}.{extension}"  # S3 keys

    method_params = {
        "Bucket": settings.AWS_S3_BUCKET_NAME,
        "Key": file_unique_name,
        "ContentType": data.content_type,
    }
    expires_in = 3600

    try:
        presigned_url = s3_client.generate_presigned_url(
            ClientMethod=client_method, Params=method_params, ExpiresIn=expires_in
        )
    except ClientError:
        raise

    return S3MediaObjectResponse(presigned_url=presigned_url, s3_key=file_unique_name)


def save_s3_media(
    data: CreateProductMediaObject,
    db: Session,
    current_user: CurrentUser,
    s3_client,
): ...
