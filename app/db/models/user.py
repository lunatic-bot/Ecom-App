from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .base import Base

class UserRole(PyEnum):
    USER = 'User'
    ADMIN = 'Admin'

## updating 

# Define the User model, representing the 'users' table in the database
class User(Base):
    __tablename__ = "users"  # Specify the table name as 'users'

    # Define the columns for the 'users' table
    user_id = Column(Integer, primary_key=True, index=True)  # Primary key for the table, with an index for better search performance
    username = Column(String, unique=True, index=True)  # Username of the user, unique and indexed for fast lookups
    email = Column(String, unique=True, index=True)  # Email of the user, also unique and indexed
    hashed_password = Column(String)  # Store the hashed password for security

    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)

    # Columns to handle password reset tokens and their expiration
    reset_token = Column(String, nullable=True)  # Token for resetting the password, can be null if no reset is requested
    reset_token_expiration = Column(DateTime, nullable=True)  # Expiration time for the reset token, can also be null

    orders = relationship("Order", back_populates="user")
    shopping_cart = relationship("ShoppingCart", back_populates="user", uselist=False)
    tokens = relationship("Token", back_populates="user")