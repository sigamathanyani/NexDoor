from sqlalchemy import (
    INTEGER,
    Column,
    ForeignKey,
    String,
    DateTime as SQLALchemyDateTime,
    func,
)
from sqlalchemy import Enum as SQLAlchemyEnum

from app.database.db import Base
from app.enums.token_type import TokenType


class VerificationTokenTable(Base):
    __tablename__ = "VerificationTokens"

    token_id = Column(INTEGER, primary_key=True, index=True)
    user_id = Column(INTEGER, ForeignKey("Users.user_id"), index=True, nullable=False)
    token_hash = Column(
        type_=String(255),
        nullable=False,
        unique=True
    )
    token_type = Column(type_=SQLAlchemyEnum(TokenType), nullable=False)
    expires_at = Column(
        name="expires_at",
        type_=SQLALchemyDateTime(timezone=True),
        nullable=False,
    )
    created_at = Column(
        name="created_at",
        type_=SQLALchemyDateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
