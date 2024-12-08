from sqlalchemy import ForeignKey, Column, UUID, Table, Integer
from sqlalchemy.orm import relationship
from .base import Base
import uuid


# Association table for Wishlist and Products
wishlist_product_association = Table(
    'wishlist_product',  # Name of the association table in the database
    Base.metadata,  # Metadata object to bind the table
    Column('wishlist_id', UUID(as_uuid=True), ForeignKey('wishlists.wishlist_id'), primary_key=True),
    # Column to store the foreign key referencing the `wishlist_id` in the `wishlists` table
    Column('product_id', UUID(as_uuid=True), ForeignKey('products.product_id'), primary_key=True)
    # Column to store the foreign key referencing the `product_id` in the `products` table
)

# ORM model for the "wishlists" table
class Wishlist(Base):
    __tablename__ = 'wishlists'  # Specifies the name of the table in the database

    # Columns
    wishlist_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Unique identifier for each wishlist, primary key with a UUID default value

    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    # Foreign key referencing the `user_id` in the `users` table, links the wishlist to a user

    # Relationships
    products = relationship(
        "Product",  # Target model to establish the relationship
        secondary=wishlist_product_association,  # Specifies the association table
        back_populates="wishlists"  # Bi-directional relationship with the `wishlists` attribute in the Product model
    )
    # Defines a many-to-many relationship between Wishlist and Product through the association table



# # Association table for Wishlist and Products
# wishlist_product_association = Table(
#     'wishlist_product', Base.metadata,
#     Column('wishlist_id', UUID(as_uuid=True), ForeignKey('wishlists.wishlist_id'), primary_key=True),
#     Column('product_id', UUID(as_uuid=True), ForeignKey('products.product_id'), primary_key=True)
# )

# class Wishlist(Base):
#     __tablename__ = 'wishlists'

#     wishlist_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)

#     # Many-to-Many Relationship with Product
#     products = relationship(
#         "Product",
#         secondary=wishlist_product_association,
#         back_populates="wishlists"
#     )


# class Wishlist(Base):
#     __tablename__ = 'wishlists'

#     wishlist_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
#     product_id = Column(UUID(as_uuid=True), ForeignKey('products.product_id'), nullable=False)

#     # Many-to-Many Relationship with Product
#     products = relationship(
#         "Product",
#         secondary=wishlist_product_association,
#         back_populates="wishlists"
#     )