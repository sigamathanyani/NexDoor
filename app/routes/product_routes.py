from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException

from app.database.db import get_db
from app.dependencies.auth_dependency import get_current_user
from app.schemas.product_schema import CreateProduct, ProductResponse, UpdateProduct
from app.schemas.user_schema import CurrentUser
from app.services.product_service import (
    create_product,
    delete_single_product,
    get_all_products,
    get_single_product,
    update_single_product,
)

from app.dependencies.aws_dependency import get_s3_client

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProductResponse)
def add_product(
    product_data: CreateProduct,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    s3_client=Depends(get_s3_client),
):
    return create_product(
        product_data, db=db, current_user=current_user, s3_client=s3_client
    )


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[ProductResponse])
def get_products_route(db: Session = Depends(get_db), s3_client=Depends(get_s3_client)):
    return get_all_products(
        db=db,
        s3_client=s3_client,
    )


@router.get(
    "/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductResponse
)
def get_product_route(
    product_id: int,
    db: Session = Depends(get_db),
    s3_client: Session = Depends(get_s3_client),
):
    product = get_single_product(db=db, s3_client=s3_client, product_id=product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Product not found"},
        )
    return product


@router.put(
    "/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductResponse
)
def update_product_route(
    product_id: int,
    product_updated: UpdateProduct,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = update_single_product(
        product_updated=product_updated,
        db=db,
        product_id=product_id,
        current_user=current_user,
    )
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "You cannot perform this operation "},
        )
    return product


@router.delete(
    "/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductResponse
)
def delete_product_route(
    product_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = delete_single_product(
        db=db, product_id=product_id, current_user=current_user
    )
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "You cannot perform this operation "},
        )
    return product
