from sqlalchemy import Column, UUID, Numeric, ForeignKey, Enum  # Import required column types for the SQLAlchemy model
from .base import Base
import uuid
from enum import Enum as PyEnum


# Enumeration to represent different payment methods
class PaymentMethod(PyEnum):
    CREDIT_CARD = 'CreditCard'  # Payment made using a credit card
    PAYPAL = 'PayPal'  # Payment made via PayPal
    BANK_TRANSFER = 'BankTransfer'  # Payment made via bank transfer

# Enumeration to represent the status of a payment
class PaymentStatus(PyEnum):
    PENDING = 'Pending'  # Payment is initiated but not yet completed
    COMPLETED = 'Completed'  # Payment has been successfully completed
    FAILED = 'Failed'  # Payment attempt failed

# ORM model for the "payments" table
class Payment(Base):
    __tablename__ = 'payments'  # Specifies the table name in the database

    # Columns
    payment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Unique identifier for the payment
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.order_id'), nullable=False)  # Foreign key to the related order
    payment_method = Column(Enum(PaymentMethod), nullable=False)  # The method used to make the payment
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)  # Current status of the payment
    amount = Column(Numeric(10, 2), nullable=False)  # Total amount of the payment (precision: 10 digits, 2 decimals)


# class PaymentMethod(PyEnum):
#     CREDIT_CARD = 'CreditCard'
#     PAYPAL = 'PayPal'
#     BANK_TRANSFER = 'BankTransfer'

# class PaymentStatus(PyEnum):
#     PENDING = 'Pending'
#     COMPLETED = 'Completed'
#     FAILED = 'Failed'

# class Payment(Base):
#     __tablename__ = 'payments'

#     payment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     order_id = Column(UUID(as_uuid=True), ForeignKey('orders.order_id'), nullable=False)
#     payment_method = Column(Enum(PaymentMethod), nullable=False)
#     payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
#     amount = Column(Numeric(10, 2), nullable=False)
