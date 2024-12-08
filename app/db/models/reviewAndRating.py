import uuid
from sqlalchemy import Column, UUID, Integer, String, ForeignKey 
from .base import Base


# ORM model for the "reviews" table
class Review(Base):
    __tablename__ = 'reviews'  # Specifies the table name in the database

    # Columns
    review_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  
    # Unique identifier for each review, automatically generated using UUID

    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)  
    # Foreign key linking to the user who submitted the review

    product_id = Column(UUID(as_uuid=True), ForeignKey('products.product_id'), nullable=False)  
    # Foreign key linking to the product being reviewed

    rating = Column(Integer, nullable=False)  
    # Numeric rating given by the user (e.g., 1-5 stars)

    comment = Column(String, nullable=True)  
    # Optional text comment provided by the user along with the rating



# class Review(Base):
#     __tablename__ = 'reviews'

#     review_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
#     product_id = Column(UUID(as_uuid=True), ForeignKey('products.product_id'), nullable=False)
#     rating = Column(Integer, nullable=False)
#     comment = Column(String, nullable=True)
