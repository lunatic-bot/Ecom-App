from sqlalchemy import Numeric, Integer, String, UUID
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
import uuid
from .wishlist import wishlist_product_association


# Association table for many-to-many relationship between products and categories
product_category_association = Table(
    'product_category', Base.metadata,  # Table name and metadata
    Column('product_id', UUID(as_uuid=True), ForeignKey('products.product_id')),  # Foreign key referencing products
    Column('category_id', UUID(as_uuid=True), ForeignKey('categories.category_id'))  # Foreign key referencing categories
)

# ORM model for the "products" table
class Product(Base):
    __tablename__ = 'products'  # Specifies the table name in the database

    # Columns
    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Unique identifier for the product
    vendor_id = Column(UUID(as_uuid=True), ForeignKey('vendors.vendor_id'), nullable=False)  # Foreign key linking to the vendor who owns the product
    name = Column(String, nullable=False)  # Name of the product
    description = Column(String, nullable=True)  # Description of the product (optional)
    price = Column(Numeric(10, 2), nullable=False)  # Price of the product (precision: 10 digits, 2 decimals)
    stock_quantity = Column(Integer, nullable=False)  # Quantity of the product available in stock
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.category_id'), nullable=False)  # Foreign key linking to a primary category

    # Relationships
    vendor = relationship("Vendor", back_populates="products")  # One-to-Many relationship linking to the Vendor model

    categories = relationship(
        "Category",  # Many-to-Many relationship linking to categories
        secondary=product_category_association,  # Uses the association table to establish the relationship
        back_populates="products"  # Bidirectional relationship with the Category model
    )

    wishlists = relationship(
        "Wishlist",  # Many-to-Many relationship linking to wishlists
        secondary=wishlist_product_association,  # Uses a separate association table for products and wishlists
        back_populates="products"  # Bidirectional relationship with the Wishlist model
    )

# ORM model for the "categories" table
class Category(Base):
    __tablename__ = 'categories'  # Specifies the table name in the database

    # Columns
    category_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Unique identifier for the category
    name = Column(String, nullable=False)  # Name of the category
    description = Column(String, nullable=True)  # Description of the category (optional)

    # Relationships
    products = relationship(
        "Product",  # Many-to-Many relationship linking to products
        secondary=product_category_association,  # Uses the association table to establish the relationship
        back_populates="categories"  # Bidirectional relationship with the Product model
    )


