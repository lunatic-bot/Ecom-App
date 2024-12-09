from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .base import Base 


# Enum to represent different user roles
class UserRole(PyEnum):
    USER = 'User'  # Regular user with basic access
    ADMIN = 'Admin'  # Administrator with elevated permissions
    VENDOR = 'Vendor'  # Vendor who can manage products and related resources


# ORM model for the "users" table
class User(Base):
    __tablename__ = "users"  # Specifies the table name in the database

    # Columns
    user_id = Column(Integer, primary_key=True, index=True)
    # Unique identifier for each user, acts as the primary key

    username = Column(String, unique=True, index=True, nullable=False)
    # Username for the user, must be unique and cannot be null

    email = Column(String, unique=True, index=True, nullable=False)
    # Email address of the user, must be unique and cannot be null

    hashed_password = Column(String, nullable=False)
    # Encrypted version of the user's password for secure storage

    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    # Role of the user (e.g., USER, ADMIN, VENDOR), defaults to USER

    # Password reset functionality
    reset_token = Column(String, nullable=True)
    # Token for resetting the user's password (optional, can be null)

    reset_token_expiration = Column(DateTime, nullable=True)
    # Expiration timestamp for the password reset token (optional, can be null)

    # Relationships
    tokens = relationship("Token", back_populates="user", lazy="dynamic")
    # Relationship with the Token model, enabling access to associated tokens
    # `lazy="dynamic"` means tokens are loaded on-demand as a query

    orders = relationship("Order", back_populates="user")
    # Relationship with the Order model, linking a user to their orders

    shopping_cart = relationship("ShoppingCart", back_populates="user")
    # Relationship with the ShoppingCart model, linking a user to their shopping cart


