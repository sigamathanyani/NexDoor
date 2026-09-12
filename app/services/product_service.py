from decimal import Decimal

from fastapi import status

from botocore.exceptions import ClientError
from sqlalchemy import UnaryExpression, and_
from sqlalchemy.orm import Session

from app.enums.media_type import MediaType
from app.enums.product_status import ProductStatus
from app.enums.sorting import SortBy, SortOrder
from app.models.media_model import ProductMediaTable
from app.models.product_model import ProductTable
from app.schemas.product_schema import CreateProduct, ProductResponse, UpdateProduct
from app.schemas.user_schema import CurrentUser
from app.exceptions.app_exception import AppException
from app.utils.error_codes import ErrorCode
from app.utils.aws_utils import get_presigned_url_helper, error_helper
from app.config import settings


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
        category=product_data.category,
    )

    db.add(new_product)
    db.flush()

    # checking if the image exist in s3 before created a DB record
    try:
        response = s3_client.head_object(
            Bucket=settings.AWS_S3_BUCKET_NAME, Key=product_data.s3_key
        )
    except ClientError as e:
        error_helper(e)

    media = response["ContentType"].split("/")[0]
    if media == "image":
        type_ = MediaType.IMAGE
    elif media == "video":
        type_ = MediaType.VIDEO
    else:
        raise AppException(
            "The media you are trying to upload is not supported. Only images and videos",
            error_code=ErrorCode.MEDIA_TYPE_NOT_SUPPORTED,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

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
        category=product_data.category,
        image=product_image_url,
    )


def get_all_products(
    query_params,
    db: Session,
    s3_client,
):
    q = (
        db.query(ProductMediaTable.s3_key, ProductTable)
        .join(ProductTable, ProductTable.product_id == ProductMediaTable.product_id)
        .where(
            ProductMediaTable.is_primary == True,
            ProductTable.product_status == ProductStatus.ACTIVE,
        )
    )

    if query_params.product_query is not None:
        param_value = query_params.product_query
        q = q.filter(
            ProductTable.product_name.ilike(f"%{param_value}%")
            | ProductTable.product_description.ilike(f"%{param_value}%"),
        )

    if query_params.product_type:
        q = q.filter(ProductTable.product_type.in_(query_params.product_type))

    if query_params.category_filter:
        q = q.filter(ProductTable.category.in_(query_params.category_filter))

    if query_params.sort_by:
        order: UnaryExpression[Decimal]
        if query_params.sort_by == SortBy.PRICE:
            if query_params.sort_order == SortOrder.ASC:
                order = ProductTable.price.asc()
            elif query_params.sort_order == SortOrder.DESC:
                order = ProductTable.price.desc()

        q = q.order_by(order)

    products = q.all()

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
                category=product.category,
                image=product_image_url,
            )
        )

    return all_products


def get_single_product(db: Session, s3_client, product_id: int):

    products = (
        db.query(ProductMediaTable.s3_key, ProductTable)
        .join(ProductTable, ProductTable.product_id == ProductMediaTable.product_id)
        .where(ProductTable.product_id == product_id)
        .all()
    )

    if not products:
        raise AppException(
            message="The product is not found",
            error_code=ErrorCode.PRODUCT_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    _, product = products[0]
    product_images = []
    for s3_key, _ in products:
        product_images.append(
            get_presigned_url_helper(
                s3_key=s3_key,
                client_method="get_object",
                s3_client=s3_client,
                content_type="image/png",
            )
        )

    return ProductResponse(
        product_id=product.product_id,
        product_name=product.product_name,
        product_description=product.product_description,
        product_type=product.product_type,
        price=product.price,
        pricing_unit=product.pricing_unit,
        category=product.category,
        image=product_images,
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
        raise AppException(
            message="You are not allowed to modify this product",
            error_code=ErrorCode.AUTH_UNAUTHORIZED,
            status_code=status.HTTP_403_FORBIDDEN,
        )

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
        category=product_to_update.category,
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
        raise AppException(
            message="You are not allowed to delete this product",
            error_code=ErrorCode.AUTH_UNAUTHORIZED,
            status_code=status.HTTP_403_FORBIDDEN,
        )

    product_to_delete.product_status = ProductStatus.INACTIVE
    db.commit()
    db.refresh(product_to_delete)

    return product_to_delete
