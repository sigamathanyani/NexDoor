from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.enums.pricing_unit import PricingUnit
from app.enums.product_status import ProductStatus
from app.enums.product_type import ProductType
from app.utils.validators import enum_validator, string_validator


class CreateProduct(BaseModel):
    name: str
    description: str
    product_type: ProductType
    price: Decimal
    pricing_unit: PricingUnit
    s3_key: str
    image_name: str

    @field_validator("name")
    def validate_name(name):
        validator = string_validator(name, "name")
        if validator is not None:
            raise ValueError(validator)
        return name

    @field_validator("description")
    def validate_description(description):
        validator = string_validator(description, "description")
        if validator is not None:
            raise ValueError(validator)
        return description
    
    @field_validator("image_name")
    def validate_image_name(image_name):
        validator = string_validator(image_name, "image_name")
        if validator is not None:
            raise ValueError(validator)
        return image_name
    
    @field_validator("s3_key")
    def validate_s3_key(s3_key):
        validator = string_validator(s3_key, "s3_key")
        if validator is not None:
            raise ValueError(validator)
        return s3_key

    @field_validator("price")
    def validate_price(price):
        if price < 1:
            raise ValueError("Price must be atleast 1")
        return price

    @field_validator("pricing_unit")
    def validate_unit(cls, pricing_unit, info):
        product_type = info.data["product_type"]
        validator = enum_validator(product_type, pricing_unit)
        if validator is not None:
            raise ValueError(validator)
        return pricing_unit

class UpdateProduct(BaseModel):
    name: str
    description: str
    product_type: ProductType
    price: Decimal
    pricing_unit: PricingUnit
    product_status: ProductStatus

    @field_validator("name")
    def validate_name(name):
        validator = string_validator(name, "name")
        if validator is not None:
            raise ValueError(validator)
        return name

    @field_validator("description")
    def validate_description(description):
        validator = string_validator(description, "description")
        if validator is not None:
            raise ValueError(validator)
        return description

    @field_validator("price")
    def validate_price(price):
        if price < 1:
            raise ValueError("Price must be atleast 1")
        return price

    @field_validator("pricing_unit")
    def validate_unit(cls, pricing_unit, info):
        product_type = info.data.get('product_type')
        if product_type is None:
            return pricing_unit
        validator = enum_validator(product_type, pricing_unit)
        if validator is not None:
            raise ValueError(validator)
        return pricing_unit


class ProductResponse(BaseModel):
    product_id: int
    name: str = Field(validation_alias='product_name')
    description: str = Field(validation_alias='product_description')
    product_type: ProductType
    price: Decimal
    pricing_unit: PricingUnit
    image: str | list[str]

    model_config = ConfigDict(from_attributes=True)