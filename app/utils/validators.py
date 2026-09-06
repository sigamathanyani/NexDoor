from fastapi import status

from app.enums.pricing_unit import PricingUnit
from app.enums.product_type import ProductType
from app.exceptions.app_exception import AppException
from app.utils.error_codes import ErrorCode


def password_validator(password: str) -> str | None:
    if len(password) < 8:
        return "Password length must be at least 8 characters"

    if not any(char.isdigit() for char in password):
        return "Password must contain at least one number"

    if not any(char.isupper() for char in password):
        return "Password must contain at least one uppercase letter"

    if not any(char.islower() for char in password):
        return "Password must contain at least one lower case"

    if not any(char in "~`!@#$%^&*()_+=-[/?.>,<]" for char in password):
        return "Password must contain at least one special character"

    return None


def string_validator(name: str, field: str) -> str | None:
    if not isinstance(name, str):
        return f"{field} must be a string"

    if len(name.strip()) < 1:
        return f"{field} cannot be empty"

    return None


def enum_validator(type_: ProductType, unit: PricingUnit) -> str | None:

    unit_dict: dict[ProductType, list[PricingUnit]] = {
        ProductType.SELL: [PricingUnit.ONE_TIME],
        ProductType.RENT: [PricingUnit.HOUR, PricingUnit.DAY, PricingUnit.WEEK],
        ProductType.SERVICE: [PricingUnit.HOUR, PricingUnit.DAY, PricingUnit.SERVICE],
    }

    if unit not in unit_dict[type_]:
        raise AppException(
            message=f"{unit.value} is not a valid pricing unit for {type_.value} product",
            error_code=ErrorCode.BAD_REQUEST,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return None
