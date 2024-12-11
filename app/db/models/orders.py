from sqlalchemy import Enum
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Numeric, String, UUID, ForeignKey  # Import required column types for the SQLAlchemy model
from .base import Base
import uuid
from enum import Enum as PyEnum


# Enumeration to represent the possible statuses of an order
class OrderStatus(PyEnum):
    CART = 'Cart'  # Represents a draft order (e.g., items in a cart, not yet placed)
    PENDING = 'Pending'  # Order has been placed but not yet shipped
    SHIPPED = 'Shipped'  # Order has been shipped but not yet delivered
    DELIVERED = 'Delivered'  # Order has been delivered to the customer
    CANCELED = 'Canceled'  # Order has been canceled

# ORM model for the "orders" table
class Order(Base):
    __tablename__ = 'orders'  # Specifies the table name in the database

    # Columns
    order_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Unique identifier for the order
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)  # ID of the user who placed the order
    total_amount = Column(Numeric(10, 2), nullable=False)  # Total cost of the order (precision: 10 digits, 2 decimals)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)  # Current status of the order
    shipping_address = Column(String, nullable=False)  # Address to which the order is being shipped
    cancellation_reason = Column(String, nullable=True)  # Reason for cancellation, if applicable

    # Relationships
    user = relationship("User", back_populates="orders")  # Relationship to the User who placed the order
    order_items = relationship("OrderItem", back_populates="order")  # List of items associated with the order

# ORM model for the "order_items" table
class OrderItem(Base):
    __tablename__ = 'order_items'  # Specifies the table name in the database

    # Columns
    order_item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Unique identifier for the order item
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.order_id'), nullable=False)  # Foreign key to the related order
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.product_id'), nullable=False)  # Foreign key to the product
    quantity = Column(Integer, nullable=False)  # Number of units of the product ordered
    price = Column(Numeric(10, 2), nullable=False)  # Price per unit of the product (precision: 10 digits, 2 decimals)

    # Relationships
    order = relationship("Order", back_populates="order_items")  # Reference to the parent order

