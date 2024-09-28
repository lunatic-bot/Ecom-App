from sqlalchemy import Column, UUID, Numeric, ForeignKey, Enum  # Import required column types for the SQLAlchemy model
from .base import Base
import uuid
from enum import Enum as PyEnum

class PaymentMethod(PyEnum):
    CREDIT_CARD = 'CreditCard'
    PAYPAL = 'PayPal'
    BANK_TRANSFER = 'BankTransfer'

class PaymentStatus(PyEnum):
    PENDING = 'Pending'
    COMPLETED = 'Completed'
    FAILED = 'Failed'

class Payment(Base):
    __tablename__ = 'payments'

    payment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.order_id'), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
