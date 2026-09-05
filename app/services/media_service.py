import uuid

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.config import settings

from app.enums.media_type import MediaType
from app.models.media_model import ProductMediaTable
from app.models.product_model import ProductTable
from app.schemas.product_media_schema import (
    ProductMediaResponse,
    S3MediaObjectResponse,
    CreateProductMediaObject,
)
from app.schemas.user_schema import CurrentUser
from app.utils.aws_utils import get_s3_key, get_presigned_url_helper

from botocore.exceptions import ClientError


# WORK WHEN UPLOADING IMAGES TO ALREADY EXISTING PRODUCT
def get_presigned_url(
    db: Session,
    product_id: int,
    current_user: CurrentUser,
    s3_client,
    client_method,
):

    product = (
        db.query(ProductTable)
        .filter(
            and_(
                ProductTable.product_id == product_id,
                ProductTable.user_id == current_user.user_id,
            )
        )
        .first()
    )

    if not product:
        return None

    product_media_count = (
        db.query(ProductMediaTable)
        .filter(ProductMediaTable.product_id == product_id)
        .count()
    )

    if product_media_count >= 5:
        return None

    s3_key = ""
    if client_method == "put_object":
        s3_key = get_s3_key()
        presigned_url = get_presigned_url_helper(
            s3_key=s3_key,
            client_method=client_method,
            s3_client=s3_client,
            content_type="image/png",
        )

    elif client_method == "get_object":
        # get the key from the db
        product_medias = (
            db.query(ProductMediaTable)
            .where(ProductMediaTable.product_id == product_id)
            .all()
        )

        get_media_urls = []
        for product_media in product_medias:
            presigned_url = get_presigned_url_helper(
                s3_key=product_media.s3_key,
                client_method=client_method,
                s3_client=s3_client,
                content_type="image/png",
            )

            get_media_urls.append(presigned_url)
        presigned_url = get_media_urls

    return S3MediaObjectResponse(presigned_url=presigned_url, s3_key=s3_key)


# WORK WHEN UPLOADING IMAGES WHEN CREATING A PRODUCT
def get_presigned_url_for_creation(
    s3_client,
    client_method,
):
    s3_key = get_s3_key()
    
    presigned_url = get_presigned_url_helper(
        s3_key=s3_key,
        client_method=client_method,
        s3_client=s3_client,
        content_type="image/png",
    )

    return S3MediaObjectResponse(presigned_url=presigned_url, s3_key=s3_key)


def save_s3_media(
    product_id: int,
    data: CreateProductMediaObject,
    db: Session,
    current_user: CurrentUser,
    s3_client,
):

    product = (
        db.query(ProductTable)
        .where(
            ProductTable.user_id == current_user.user_id,
            ProductTable.product_id == product_id,
        )
        .first()
    )

    if product is None:
        return

    product_media_count = (
        db.query(ProductMediaTable)
        .filter(ProductMediaTable.product_id == product_id)
        .count()
    )

    if product_media_count >= 5:
        return None

    try:
        response = s3_client.head_object(
            Bucket=settings.AWS_S3_BUCKET_NAME, Key=data.s3_key
        )
    except ClientError:
        raise

    media = response["ContentType"].split("/")[0]
    if media == "image":
        type_ = MediaType.IMAGE
    elif media == "video":
        type_ = MediaType.VIDEO
    else:
        raise

    product_media = ProductMediaTable(
        product_id=product_id,
        file_name=data.name,
        s3_key=data.s3_key,
        media_type=type_,
        is_primary=data.is_primary,
    )

    # add the record to the db
    db.add(product_media)

    if data.is_primary:
        old_primary_img = (
            db.query(ProductMediaTable)
            .where(
                ProductMediaTable.product_id == product_id,
                ProductMediaTable.is_primary == True,
            )
            .first()
        )

        if old_primary_img is not None:
            old_primary_img.is_primary = False

    db.commit()
    db.refresh(product_media)

    return ProductMediaResponse(name=data.name)
