from app.database.db import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, DateTime as SQLALchemyDateTime, Text, func
from sqlalchemy import Enum as SQLAlchemyEnum

from app.enums.media_type import MediaType

class ProductMediaTable(Base):
    media_id = Column(Integer, primary_key=True, index=True, nullable=False)
    product_id = Column(Integer, ForeignKey("Products.product_id"), nullable=False, index=True)
    s3_key = Column(name='s3_key', type_=Text, nullable=False, unique=True,)
    media_type = Column(name='media_type', type_=SQLAlchemyEnum(MediaType), nullable=False)
    is_primary = Column(name='is_primary_image', type_=Boolean, nullable=False)
    created_at = Column(name='created_at', type_=SQLALchemyDateTime(timezone=True,), nullable=False, server_default=func.now())