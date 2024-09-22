from sqlalchemy.orm import Session  # Import SQLAlchemy session for interacting with the database
from app.models.users import User  # Import the User model
from app.core.auth import verify_password  # Import function to verify password from the auth module
from app.core.auth import get_password_hash  # Import function to hash passwords from the auth module

# Function to create a new user in the database
def create_user_in_db(db: Session, username: str, email: str, password: str) -> User:
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
    db.commit()
    # Refresh the user instance to reflect any auto-generated fields (e.g., ID)
    db.refresh(new_user)
    
    return new_user  # Return the created user instance

# Function to retrieve a user by their email
def get_user_by_mail(db: Session, email: str):
    """
    Fetches a user from the database based on their email.
    Args:
        db (Session): SQLAlchemy database session.
        email (str): The email of the user to be fetched.
    Returns:
        User: The user instance if found, else None.
    """
    return db.query(User).filter(User.email == email).first()

# Function to authenticate a user by email and password
def authenticate_user(db: Session, email: str, password: str):
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
    user = get_user_by_mail(db, email=email)
    
    # Return False if the user is not found
    if not user:
        return False
    
    # Verify the password, return False if it doesn't match
    if not verify_password(password, user.hashed_password):
        return False
    
    # Return the authenticated user if successful
    return user

# Function to retrieve a user by their reset token
def get_user_by_token(db: Session, token: str):
    """
    Fetches a user from the database based on their password reset token.
    Args:
        db (Session): SQLAlchemy database session.
        token (str): The reset token of the user.
    Returns:
        User: The user instance if found, else None.
    """
    return db.query(User).filter(User.reset_token == token).first()
