from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession  # Import SQLAlchemy asyncsession for interacting with the database
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone

from schemas.users import UserUpdate
from schemas.users import UserResponse
from db.models.users import User # Import the User model
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
    hashed_password = await get_password_hash(password)
    
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


# Asynchronous function to delete a user from the database with exception handling
async def delete_user(db: AsyncSession, user_id: int):
    try:
        # Fetch the user from the database using the provided `user_id`
        result = await db.execute(select(User).filter(User.user_id == int(user_id)))
        
        # Fetch the first matching user (or None if no user is found)
        user = result.scalars().first()

        # If no user is found, raise a 404 HTTP exception indicating that the user was not found
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # If the user is found, delete the user from the database
        await db.delete(user)

        # Commit the changes to the database to persist the deletion
        await db.commit()

        # Return the deleted user object
        # The return value allows confirming the deleted user's details
        return user

    except Exception as e:
        # Log the error message if something goes wrong
        # You can replace the print statement with actual logging (e.g., `logging.error(str(e))`)
        print(f"Error occurred while deleting user with ID {user_id}: {str(e)}")

        # Raise a generic HTTPException with a 500 status code if an unexpected error occurs
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while deleting the user")



# Asynchronous function to fetch all users from the database with exception handling
async def get_all_users(db: AsyncSession):
    try:
        # Execute a query to select all users from the 'User' table
        result = await db.execute(select(User))
        
        # Fetch all user records from the query result and convert them to a list
        users = result.scalars().all()

        # Return the list of users
        return users

    except Exception as e:
        # Log the error message if something goes wrong during the database operation
        # Replace `print` with an actual logging mechanism for production (e.g., `logging.error()`)
        print(f"Error occurred while fetching users: {str(e)}")

        # Raise an HTTPException with a 500 status code indicating an internal server error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching users")



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


# Asynchronous function to fetch a token entry for a specific user by refresh token
async def get_token_for_user(db: AsyncSession, refresh_token: str, user_id: int):
    try:
        # Create a select statement to fetch the token for the specified user and refresh token
        stmt = select(Token).where(Token.refresh_token == refresh_token, Token.user_id == int(user_id))
        
        # Execute the query against the database to get the result
        result = await db.execute(stmt)
        
        # Fetch the first token entry from the result (if any)
        token_entry = result.scalars().first()
        
        # Return the token entry if found, or None if not
        return token_entry

    except Exception as e:
        # Log the error message in case of any exception during the database operation
        # Replace `print` with actual logging for production (e.g., `logging.error()`)
        print(f"Error occurred while fetching token for user {user_id}: {str(e)}")

        # Raise an HTTPException with a 500 status code indicating an internal server error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching the token")



# Asynchronous function to update a user's details
async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate):
    try:
        # Fetch the user from the database using the provided user_id
        result = await db.execute(select(User).filter(User.user_id == int(user_id)))
        user = result.scalars().first()

        # If the user is not found, raise a 404 HTTPException
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Update user details by iterating over the fields provided in the user_update object
        # The `exclude_unset=True` ensures only the fields provided in the request are updated
        for key, value in user_update.dict(exclude_unset=True).items():
            setattr(user, key, value)

        # Commit the changes to the database
        await db.commit()

        # Refresh the user instance to reflect the updated data
        await db.refresh(user)

        # Return the updated user object
        return user

    except Exception as e:
        # Log the error message in case of any exception during the database operation
        # In production, replace `print` with actual logging (e.g., `logging.error()`)
        print(f"Error occurred while updating user {user_id}: {str(e)}")

        # Raise an HTTPException with a 500 status code indicating an internal server error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while updating the user")


# Asynchronous function to retrieve a user by their reset token
async def get_user_by_token(db: AsyncSession, token: str):
    try:
        # Execute a database query to find the user associated with the given reset token
        result = await db.execute(select(User).filter(User.reset_token == token))
        
        # Return the first user found or None if no user matches the reset token
        user = result.scalars().first()

        # If no user is found, raise a 404 HTTPException indicating that the token is invalid
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid reset token")

        # Return the user object
        return user

    except Exception as e:
        # Log the error message in case of an unexpected error (replace `print` with actual logging in production)
        print(f"Error occurred while retrieving user by reset token: {str(e)}")
        
        # Raise an HTTPException with a 500 status code indicating an internal server error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while retrieving the user")

