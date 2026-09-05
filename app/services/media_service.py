import uuid

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.config import settings

from app.enums.media_type import MediaType
from app.models.media_model import ProductMediaTable
from app.models.product_model import ProductTable
from app.schemas.product_media_schema import (
    ProductMediaResponse,
    RequestPresignedUrlData,
    S3MediaObjectResponse,
    CreateProductMediaObject,
)
from app.schemas.user_schema import CurrentUser

from botocore.exceptions import ClientError


def _presigned_url(s3_key: str, client_method, s3_client, content_type):
    method_params = {
        "Bucket": settings.AWS_S3_BUCKET_NAME,
        "Key": s3_key,  # will be different for get - we have it in the DB
    }
    if client_method == "put_object":
        method_params["ContentType"] = content_type

    expires_in = 3600

    try:
        presigned_url = s3_client.generate_presigned_url(
            ClientMethod=client_method, Params=method_params, ExpiresIn=expires_in
        )
    except ClientError:
        raise

    return presigned_url


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
        extension = "png"  # data.content_type.split("/")[1]
        file_id = str(uuid.uuid4())
        file_unique_name = f"products/{product_id}/{file_id}.{extension}"  # S3 keys
        s3_key = file_unique_name
        presigned_url = _presigned_url(
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
        # s3_key = product.
        media_urls = []
        for product_media in product_medias:
            presigned_url = _presigned_url(
                s3_key=product_media.s3_key,
                client_method=client_method,
                s3_client=s3_client,
                content_type="image/png",
            )

            media_urls.append(presigned_url)
        
            # res = s3_client.get_object(
            #         Bucket=settings.AWS_S3_BUCKET_NAME, Key=product_media.s3_key
            #     )
            # byt = res['Body'].read()
            # input(byt)
        presigned_url = media_urls

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
