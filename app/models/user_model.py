from sqlalchemy import Boolean, Column, Integer, String

from app.database.db import Base


class UserTable(Base):
    __tablename__ = "Users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(name="first_name", type_=String(50), nullable=False)
    surname = Column(name="last_name", type_=String(50), nullable=False)
    email = Column(
        name="email",
        type_=String(100),
        nullable=False,
        unique=True,
    )
    hash_password = Column(name="hash_password", type_=String(255), nullable=False)
    is_verified = Column(name="is_verified", type_=Boolean, default=False)
