from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.enums.product_status import ProductStatus
from app.models.product_model import ProductTable
from app.schemas.product_schema import CreateProduct, ProductResponse, UpdateProduct
from app.schemas.user_schema import CurrentUser


def create_product(product_data: CreateProduct, db: Session, current_user: CurrentUser):
    new_product = ProductTable(
        user_id=current_user.user_id,
        product_name=product_data.name,
        product_description=product_data.description,
        product_type=product_data.product_type,
        price=product_data.price,
        pricing_unit=product_data.pricing_unit,
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return ProductResponse(
        product_id=new_product.product_id,
        product_name=new_product.product_name,
        product_description=new_product.product_description,
        product_type=new_product.product_type,
        price=new_product.price,
        pricing_unit=new_product.pricing_unit,
    )


def get_all_products(
    db: Session,
):
    return (
        db.query(ProductTable)
        .filter(ProductTable.product_status == ProductStatus.ACTIVE)
        .all()
    )

def get_single_product(db: Session, product_id: int):
    return (
        db.query(ProductTable)
        .filter(
            and_(
                ProductTable.product_id == product_id,
                ProductTable.product_status == ProductStatus.ACTIVE,
            )
        )
        .first()
    )

def update_single_product(product_updated: UpdateProduct, db: Session, product_id: int, current_user: CurrentUser):
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
    
    product_to_update.product_name=product_updated.name
    product_to_update.product_description=product_updated.description
    product_to_update.product_type=product_updated.product_type
    product_to_update.price=product_updated.price
    product_to_update.pricing_unit=product_updated.pricing_unit
    product_to_update.product_status=product_updated.product_status

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

    product_to_delete.product_status=ProductStatus.INACTIVE
    db.commit()
    db.refresh(product_to_delete)
    
    return product_to_delete
