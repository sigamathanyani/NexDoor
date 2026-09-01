from typing import Any
import uuid

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.enums.content_type import ContentType
from app.models.media_model import ProductMediaTable
from app.models.product_model import ProductTable
from app.schemas.user_schema import CurrentUser

from botocore.exceptions import ClientError


def upload_media(
    db: Session,
    product_id: int,
    content_type: ContentType,
    current_user: CurrentUser,
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

    extension = content_type.name.split("/")[1]
    file_id = str(uuid.uuid4())
    file_unique_name = f"products/{product_id}/{file_id}.{extension}"
    

def get_presigned_url(s3_client, client_method, method_params, expires_in):
    
    try:
        presigned_url = s3_client.generate_presigned_url(
            ClientMethod=client_method,
            MethodParams=method_params,
            ExpiresIn=expires_in
        )
    except ClientError:
        raise ClientError("Couldnt get the presigned url")
    
    return presigned_url
