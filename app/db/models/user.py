from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .base import Base
# from .token import Token


class UserRole(PyEnum):
    USER = 'User'
    ADMIN = 'Admin'

## updating 
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)

    # For password reset
    reset_token = Column(String, nullable=True)
    reset_token_expiration = Column(DateTime, nullable=True)

    # Relationships
    tokens = relationship("Token", back_populates="user", lazy="dynamic")

