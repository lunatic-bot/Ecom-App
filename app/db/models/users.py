from sqlalchemy import Column, Integer, String, DateTime  # Import required column types for the SQLAlchemy model
from sqlalchemy.orm import relationship  # Import relationship to define associations between tables
from datetime import datetime  # Import datetime for handling time fields
from pytz import timezone  # Import timezone for setting a specific time zone
from app.db.database import Base  # Import the base class for SQLAlchemy models

# Define the User model, representing the 'users' table in the database
class User(Base):
    __tablename__ = "users"  # Specify the table name as 'users'

    # Define the columns for the 'users' table
    id = Column(Integer, primary_key=True, index=True)  # Primary key for the table, with an index for better search performance
    username = Column(String, unique=True, index=True)  # Username of the user, unique and indexed for fast lookups
    email = Column(String, unique=True, index=True)  # Email of the user, also unique and indexed
    hashed_password = Column(String)  # Store the hashed password for security

    # Timestamp for when the user account was created, with the default set to the current time in the 'Asia/Kolkata' timezone
    creation_time = Column(DateTime, default=datetime.now(timezone("Asia/Kolkata")))

    # Columns to handle password reset tokens and their expiration
    reset_token = Column(String, nullable=True)  # Token for resetting the password, can be null if no reset is requested
    reset_token_expiration = Column(DateTime, nullable=True)  # Expiration time for the reset token, can also be null

    # Relationship with the TodoItem model
    todos = relationship("TodoItem", back_populates="owner", cascade="all, delete-orphan")  
    # Defines a one-to-many relationship where a user can have many todos.
    # The 'cascade' option ensures that if a user is deleted, all their associated todos are also deleted.
