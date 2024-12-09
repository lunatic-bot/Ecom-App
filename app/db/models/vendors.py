from sqlalchemy import Column, String, UUID 
from sqlalchemy.orm import relationship 
from .base import Base
import uuid


# ORM model for the "vendors" table
class Vendor(Base):
    __tablename__ = 'vendors'  # Specifies the name of the table in the database

    # Columns
    vendor_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Unique identifier for each vendor, primary key with a UUID default value

    vendor_name = Column(String, nullable=False)
    # Name of the vendor, cannot be null

    email = Column(String, unique=True, nullable=False)
    # Email address of the vendor, must be unique and cannot be null

    phone = Column(String, nullable=False)
    # Contact phone number of the vendor, cannot be null

    address = Column(String, nullable=True)
    # Address of the vendor, optional and can be null

    # Relationships
    products = relationship("Product", back_populates="vendor")
    # Relationship with the Product model, links the vendor to the products they supply

