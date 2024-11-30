from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
# from .user import User


class Token(Base):
    # Define the table name for the Token model
    __tablename__ = "tokens"

    # Primary key: Unique identifier for each token record
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key: Links the token to the user who owns it (references `user_id` in the "users" table)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    # Token string: Stores the refresh token, which is unique for each user and required for token refresh
    refresh_token = Column(String, unique=True, nullable=False)

    # Expiration time: Stores the date and time when the refresh token will expire
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    # This establishes a relationship to the "User" table.
    # The `back_populates` attribute ensures bidirectional relationship between Token and User models.
    user = relationship("User", back_populates="tokens")

