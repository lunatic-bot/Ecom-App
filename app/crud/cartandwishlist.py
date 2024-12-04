from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession  # Import SQLAlchemy asyncsession for interacting with the database
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone

from schemas.users import UserUpdate
from schemas.users import UserResponse
from app.db.models.users import User # Import the User model
from db.models.token import Token # Import the User model
from core.auth import verify_password  # Import function to verify password from the auth module
from core.auth import get_password_hash  # Import function to hash passwords from the auth module


