from sqlalchemy import Column, Integer, UUID, ForeignKey 
from sqlalchemy.orm import relationship
from .base import Base
import uuid


# ORM model for the "shopping_carts" table
class ShoppingCart(Base):
    __tablename__ = 'shopping_carts'  # Specifies the table name in the database

    # Columns
    cart_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Unique identifier for each shopping cart, automatically generated using UUID

    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    # Foreign key linking the shopping cart to the user who owns it

    # Relationships
    user = relationship("User", back_populates="shopping_cart")
    # Establishes a relationship with the User table, allowing access to the user details
    # This also enables bidirectional association with the "shopping_cart" attribute on the User model


# ORM model for the "cart_items" table
class CartItem(Base):
    __tablename__ = 'cart_items'  # Specifies the table name in the database

    # Columns
    cart_item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Unique identifier for each cart item, automatically generated using UUID

    cart_id = Column(UUID(as_uuid=True), ForeignKey('shopping_carts.cart_id'), nullable=False)
    # Foreign key linking the cart item to a specific shopping cart

    product_id = Column(UUID(as_uuid=True), ForeignKey('products.product_id'), nullable=False)
    # Foreign key linking the cart item to a specific product

    quantity = Column(Integer, nullable=False)
    # Number of units of the product in the shopping cart



# class ShoppingCart(Base):
#     __tablename__ = 'shopping_carts'

#     cart_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
#     user = relationship("User", back_populates="shopping_cart")


# class CartItem(Base):
#     __tablename__ = 'cart_items'

#     cart_item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     cart_id = Column(UUID(as_uuid=True), ForeignKey('shopping_carts.cart_id'), nullable=False)
#     product_id = Column(UUID(as_uuid=True), ForeignKey('products.product_id'), nullable=False)
#     quantity = Column(Integer, nullable=False)
