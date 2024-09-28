from sqlalchemy import ForeignKey, Column, UUID 
from base import Base
import uuid

class Wishlist(Base):
    __tablename__ = 'wishlists'

    wishlist_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.product_id'), nullable=False)
