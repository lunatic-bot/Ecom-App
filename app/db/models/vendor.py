from sqlalchemy import Column, String, UUID  
from .base import Base
import uuid

class Vendor(Base):
    __tablename__ = 'vendors'

    vendor_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=True)
