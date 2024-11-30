from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy import Column, DateTime, func


# The `Base` class is a base class for all models that should have 
# common timestamp fields. This class uses SQLAlchemy's declarative 
# base system to allow automatic table mapping.
@as_declarative()
class Base:
    # The `created_at` column will automatically store the timestamp 
    # when a new record is created. The `default=func.now()` sets 
    # this value to the current time when the record is first inserted.
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # The `updated_at` column will store the timestamp when a record 
    # is updated. The `onupdate=func.now()` ensures that the timestamp 
    # will be updated automatically whenever the record is modified.
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # The `deleted_at` column is for soft deletion of records. 
    # It will store the timestamp when a record is marked as deleted.
    # This column is nullable because records that are not deleted 
    # will have a `NULL` value in this field.
    deleted_at = Column(DateTime(timezone=True), nullable=True)
