import uuid
from sqlalchemy import Column, UUID, Integer, String, ForeignKey 
from .base import Base


class Review(Base):
    __tablename__ = 'reviews'

    review_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.product_id'), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)
