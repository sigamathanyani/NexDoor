from decimal import Decimal

from pydantic import BaseModel, field_validator

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
    status: ProductStatus
    
    @field_validator('name')
    def validate_name(name):
        validator = string_validator(name)
        if validator is not None:
            raise ValueError(validator)
        return name
    
    @field_validator('description')
    def validate_description(description):
        validator = string_validator(description)
        if validator is not None:
            raise ValueError(validator)
        return description
    
    @field_validator('price')
    def validate_price(price):
        if price < 1:
            raise ValueError("Price must be atleast 1")
        return price
    
    @field_validator('pricing_unit')
    def validate_unit(self, pricing_unit, info):
        product_type = info.data['product_type']
        validator = enum_validator(product_type, pricing_unit)
        if validator is not None:
            raise ValueError(validator)
        return pricing_unit
