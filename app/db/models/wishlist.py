from sqlalchemy import ForeignKey, Column, UUID, Table, Integer
from sqlalchemy.orm import relationship
from .base import Base
import uuid


# Association table for Wishlist and Products
wishlist_product_association = Table(
    'wishlist_product', Base.metadata,
    Column('wishlist_id', UUID(as_uuid=True), ForeignKey('wishlists.wishlist_id'), primary_key=True),
    Column('product_id', UUID(as_uuid=True), ForeignKey('products.product_id'), primary_key=True)
)

class Wishlist(Base):
    __tablename__ = 'wishlists'

    wishlist_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.product_id'), nullable=False)

    # Many-to-Many Relationship with Product
    products = relationship(
        "Product",
        secondary=wishlist_product_association,
        back_populates="wishlists"
    )