from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession  # Import SQLAlchemy asyncsession for interacting with the database
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone

from schemas.users import UserUpdate
from schemas.users import UserResponse
from db.models.user import User # Import the User model
from db.models.token import Token # Import the User model
from core.auth import verify_password  # Import function to verify password from the auth module
from core.auth import get_password_hash  # Import function to hash passwords from the auth module

# Function to create a new user in the database
async def create_user_in_db(db: AsyncSession, username: str, email: str, password: str) -> User:
    """
    Creates a new user in the database.
    Args:
        db (Session): SQLAlchemy database session.
        username (str): The username of the new user.
        email (str): The email of the new user.
        password (str): The password of the new user (to be hashed).
    Returns:
        User: The created user instance.
    """
    # Hash the user's password before storing it in the database
    hashed_password = get_password_hash(password)
    
    # Create a new user instance
    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password  # Store the hashed password
    )
    
    # Add the new user to the session and commit the transaction to save it in the database
    db.add(new_user)
    await db.commit()
    # Refresh the user instance to reflect any auto-generated fields (e.g., ID)
    await db.refresh(new_user)

    return new_user
    
    # return UserResponse.from_orm(new_user)  # Return the created user instance

# Function to retrieve a user by their email
async def get_user_by_mail(db: AsyncSession, email: str):
    """
    Fetches a user from the database based on their email.
    Args:
        db (Session): SQLAlchemy database session.
        email (str): The email of the user to be fetched.
    Returns:
        User: The user instance if found, else None.
    """
    # return db.query(User).filter(User.email == email).first()
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

# Function to authenticate a user by email and password
async def authenticate_user(db: AsyncSession, email: str, password: str):
    """
    Authenticates a user by verifying their email and password.
    Args:
        db (Session): SQLAlchemy database session.
        email (str): The email of the user.
        password (str): The plain text password of the user.
    Returns:
        User: The authenticated user instance if successful, else False.
    """
    # Fetch the user by email
    user = await get_user_by_mail(db, email=email)
    
    # Return False if the user is not found
    if not user:
        return False
    
    # Verify the password, return False if it doesn't match
    if not verify_password(password, user.hashed_password):
        return False
    
    # Return the authenticated user if successful
    return user

async def delete_user(db:AsyncSession, user_id: int):
    # Fetch user
    result = await db.execute(select(User).filter(User.user_id == int(user_id)))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Delete user
    await db.delete(user)
    await db.commit()

    return user


async def get_all_users(db:AsyncSession):
    # Fetch all users
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


async def save_refresh_token(
    db: AsyncSession, refresh_token: str, user_id: int, expires_in_minutes: int
) -> Token:
    """
    Save a refresh token to the database.

    Args:
        db (AsyncSession): The database session.
        user_id (int): The ID of the user.
        refresh_token (str): The refresh token string.
        expires_at (datetime): The expiration time of the refresh token.

    Returns:
        Token: The created Token instance.

    Raises:
        ValueError: If there is an issue saving the token.
    """
    expires = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)

    new_token = Token(
        user_id=user_id,
        refresh_token=refresh_token,
        expires_at=expires,
    )

    try:
        db.add(new_token)  # Add the new token to the session
        await db.commit()  # Commit the transaction
        await db.refresh(new_token)  # Refresh to get the updated instance
        return new_token
    except IntegrityError:
        await db.rollback()  # Rollback in case of an error
        raise ValueError("Error saving token to the database: Refresh token might already exist.")


async def get_token_for_user(db: AsyncSession, refresh_token: str, user_id:int):
    stmt = select(Token).where(Token.refresh_token == refresh_token, Token.user_id == int(user_id))
    result = await db.execute(stmt)
    token_entry = result.scalars().first()
    return token_entry


async def update_user(db: AsyncSession, user_id:int, user_update:UserUpdate ):
    # Fetch user
    result = await db.execute(select(User).filter(User.user_id == int(user_id)))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update user details
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)

    return user


# Function to retrieve a user by their reset token
async def get_user_by_token(db: AsyncSession, token: str):
    """
    Fetches a user from the database based on their password reset token.
    Args:
        db (Session): SQLAlchemy database session.
        token (str): The reset token of the user.
    Returns:
        User: The user instance if found, else None.
    """
    # return await db.query(User).filter(User.reset_token == token).first()
    result = await db.execute(select(User).filter(User.reset_token == token))
    return result.scalars().first()
