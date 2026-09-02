from app.database.db import Base
from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, DateTime as SQLALchemyDateTime, String, Text, func
from sqlalchemy import Enum as SQLAlchemyEnum

from app.enums.media_type import MediaType

class ProductMediaTable(Base):
    __tablename__ = 'ProductMedia'
    
    media_id = Column(Integer, primary_key=True, index=True, nullable=False)
    product_id = Column(Integer, ForeignKey("Products.product_id"), nullable=False, index=True)
    s3_key = Column(name='s3_key', type_=Text, nullable=False,)
    media_type = Column(name='media_type', type_=SQLAlchemyEnum(MediaType), nullable=False)
    is_primary = Column(name='is_primary_image', type_=Boolean, nullable=False)
    created_at = Column(name='created_at', type_=SQLALchemyDateTime(timezone=True,), nullable=False, server_default=func.now())
    
    __table_args__ = (
        Index('idx_unique_s3_key', 's3_key', unique=True, mysql_length=300),
    )