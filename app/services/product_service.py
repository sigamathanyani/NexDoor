from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.enums.media_type import MediaType
from app.enums.product_status import ProductStatus
from app.models.media_model import ProductMediaTable
from app.models.product_model import ProductTable
from app.schemas.product_media_schema import CreateProductMediaObject
from app.schemas.product_schema import CreateProduct, ProductResponse, UpdateProduct
from app.schemas.user_schema import CurrentUser
from app.utils.aws_utils import get_s3_key, get_presigned_url_helper
from app.config import settings

from botocore.exceptions import ClientError


def create_product(
    product_data: CreateProduct,
    db: Session,
    current_user: CurrentUser,
    s3_client,
):
    new_product = ProductTable(
        user_id=current_user.user_id,
        product_name=product_data.name,
        product_description=product_data.description,
        product_type=product_data.product_type,
        price=product_data.price,
        pricing_unit=product_data.pricing_unit,
    )

    db.add(new_product)
    db.flush()

    # checking if the image exist in s3 before created a DB record
    try:
        response = s3_client.head_object(
            Bucket=settings.AWS_S3_BUCKET_NAME, Key=product_data.s3_key
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
        product_id=new_product.product_id,
        file_name=product_data.name,
        s3_key=product_data.s3_key,
        media_type=type_,
        is_primary=True,
    )

    product_image_url = get_presigned_url_helper(
        s3_key=product_data.s3_key,
        client_method="get_object",
        s3_client=s3_client,
        content_type="image/png",
    )

    db.add(product_media)
    db.commit()
    db.refresh(product_media)

    return ProductResponse(
        product_id=new_product.product_id,
        product_name=new_product.product_name,
        product_description=new_product.product_description,
        product_type=new_product.product_type,
        price=new_product.price,
        pricing_unit=new_product.pricing_unit,
        image=product_image_url,
    )


def get_all_products(
    db: Session,
    s3_client,
):
    products = (
        db.query(ProductMediaTable.s3_key, ProductTable)
        .join(ProductTable, ProductTable.product_id == ProductMediaTable.product_id)
        .where(
            ProductMediaTable.is_primary == True,
        )
        .all()
    )

    all_products = []

    for s3_key, product in products:
        product_image_url = get_presigned_url_helper(
            s3_key=s3_key,
            client_method="get_object",
            s3_client=s3_client,
            content_type="image/png",
        )

        all_products.append(
            ProductResponse(
                product_id=product.product_id,
                product_name=product.product_name,
                product_description=product.product_description,
                product_type=product.product_type,
                price=product.price,
                pricing_unit=product.pricing_unit,
                image=product_image_url,
            )
        )

    return all_products


def get_single_product(db: Session, s3_client, product_id: int):

    s3_key, product = (
        db.query(ProductMediaTable.s3_key, ProductTable)
        .join(ProductTable, ProductTable.product_id == ProductMediaTable.product_id)
        .where(
            ProductMediaTable.is_primary == True, ProductTable.product_id == product_id
        )
        .first()
    )

    product_image_url = get_presigned_url_helper(
        s3_key=s3_key,
        client_method="get_object",
        s3_client=s3_client,
        content_type="image/png",
    )

    return ProductResponse(
        product_id=product.product_id,
        product_name=product.product_name,
        product_description=product.product_description,
        product_type=product.product_type,
        price=product.price,
        pricing_unit=product.pricing_unit,
        image=product_image_url,
    )


def update_single_product(
    product_updated: UpdateProduct,
    db: Session,
    product_id: int,
    current_user: CurrentUser,
):
    product_to_update = (
        db.query(ProductTable)
        .filter(
            and_(
                ProductTable.product_id == product_id,
                ProductTable.user_id == current_user.user_id,
            )
        )
        .first()
    )

    if product_to_update is None:
        return None

    product_to_update.product_name = product_updated.name
    product_to_update.product_description = product_updated.description
    product_to_update.product_type = product_updated.product_type
    product_to_update.price = product_updated.price
    product_to_update.pricing_unit = product_updated.pricing_unit
    product_to_update.product_status = product_updated.product_status

    db.commit()
    db.refresh(product_to_update)

    return ProductResponse(
        product_id=product_to_update.product_id,
        product_name=product_to_update.product_name,
        product_description=product_to_update.product_description,
        product_type=product_to_update.product_type,
        price=product_to_update.price,
        pricing_unit=product_to_update.pricing_unit,
    )


def delete_single_product(db: Session, product_id: int, current_user: CurrentUser):
    product_to_delete = (
        db.query(ProductTable)
        .filter(
            and_(
                ProductTable.product_id == product_id,
                ProductTable.user_id == current_user.user_id,
            )
        )
        .first()
    )

    if product_to_delete is None:
        return None

    product_to_delete.product_status = ProductStatus.INACTIVE
    db.commit()
    db.refresh(product_to_delete)

    return product_to_delete
