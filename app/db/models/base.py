from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy import Column, DateTime, func
import pytz
from datetime import datetime

IST = pytz.timezone('Asia/Kolkata')

@as_declarative()
class Base:
    created_at = Column(DateTime(timezone=True), default=datetime.now(IST))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
