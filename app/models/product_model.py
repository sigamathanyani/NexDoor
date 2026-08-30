
from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, DateTime as SQLALchemyDateTime, func

from app.database.db import Base
from app.enums.pricing_unit import PricingUnit
from app.enums.product_status import ProductStatus
from app.enums.product_type import ProductType
from sqlalchemy import Enum as SQLAlchemyEnum

class ProductTable(Base):
    __tablename__ = 'Products'
    
    product_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("Users.user_id", ), nullable=False, index=True)
    product_name = Column(name='name', type_=String(50), nullable=False, unique=False)
    product_description = Column(name='description', type_=String(255), nullable=False, unique=False)
    product_type = Column(name='type', type_=SQLAlchemyEnum(ProductType), nullable=False)
    price = Column(name='price', type_=Numeric(10,2), nullable=False)
    pricing_unit = Column(name='pricing_unit', type_=SQLAlchemyEnum(PricingUnit), nullable=False)
    product_status = Column(name='status', type_=SQLAlchemyEnum(ProductStatus), nullable=False, default=ProductStatus.ACTIVE)
    created_at = Column(name='created_at', type_=SQLALchemyDateTime(timezone=True,), nullable=False, server_default=func.now())