from sqlalchemy import Numeric, Integer, String, UUID
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
import uuid
from .wishlist import wishlist_product_association


product_category_association = Table(
    'product_category', Base.metadata,
    Column('product_id', UUID(as_uuid=True), ForeignKey('products.product_id')),
    Column('category_id', UUID(as_uuid=True), ForeignKey('categories.category_id'))
)


class Product(Base):
    __tablename__ = 'products'

    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey('vendors.vendor_id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.category_id'), nullable=False)

    vendor = relationship("Vendor", back_populates="products")

    categories = relationship(
        "Category",
        secondary=product_category_association,
        back_populates="products"
    )


    # Many-to-Many Relationship with Wishlist
    wishlists = relationship(
        "Wishlist",
        secondary=wishlist_product_association,
        back_populates="products"
    )

class Category(Base):
    __tablename__ = 'categories'

    category_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    products = relationship(
        "Product",
        secondary=product_category_association,
        back_populates="categories"
    )