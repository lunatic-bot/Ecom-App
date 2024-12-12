# auth.py
from passlib.context import CryptContext  # type: ignore # Importing password encryption library
from fastapi import Depends, HTTPException, status  # Importing FastAPI dependencies for handling HTTP exceptions and status codes
from datetime import datetime, timedelta, timezone
# from pytz import timezone  # Importing timezone utilities for time zone handling
from jose import JWTError, jwt  # type: ignore # Importing JWT (JSON Web Token) utilities for token creation and verification
from fastapi.security import OAuth2PasswordBearer  # Importing OAuth2PasswordBearer for token authentication
from sqlalchemy.future import select

# from crud.users import 
from db.database import get_db  # Importing database dependency for session management
from db.models.users import User  # Importing the User model from the database models
from sqlalchemy.ext.asyncio import AsyncSession
# from jwt import PyJWTError


# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Password hashing context setup using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "57168498522b9b42531f34be15dcd8d7e1a5fe14261c7d80e82cb9cdac26bd6b"  # Secret key used for signing JWTs
ALGORITHM = "HS256"  # Algorithm used for encoding JWTs
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Access token expiration time in minutes



async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if the plain password matches the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

async def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Retrieve the current user based on the provided JWT token.

    Args:
        db (AsyncSession): The database session dependency for querying the database.
        token (str): The JWT token extracted from the Authorization header using `oauth2_scheme`.

    Returns:
        User: The user object fetched from the database.

    Raises:
        HTTPException: If the token is invalid, expired, or the user does not exist.
    """
    try:
        # Decode the JWT token to extract the payload.
        # `SECRET_KEY` and `ALGORITHM` must match the settings used during token creation.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract the user ID from the payload. This should correspond to the 'sub' claim.
        user_id: int = payload.get("sub")
        
        # If the 'sub' claim is missing, raise an Unauthorized error.
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except JWTError:
        # If the token decoding fails or is invalid, raise an Unauthorized error.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # Query the database to fetch the user with the given user ID.
    result = await db.execute(select(User).filter(User.user_id == int(user_id)))
    user = result.scalars().first()
    
    # If no user is found in the database, raise a Not Found error.
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Return the user object if everything is successful.
    return user


async def is_superuser(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")

async def is_vendor(current_user: User = Depends(get_current_user)):
    if current_user.role != "vendor":
        raise HTTPException(status_code=403, detail="Only vendors can perform this action")

async def is_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can perform this action")




async def create_access_token(data: dict, expires_in_minutes: int):
    """
    Create a JWT token with a specified expiration time.

    Args:
        data (dict): Payload data for the token.
        expires_in_minutes (int): Token expiration time in minutes.

    Returns:
        str: Encoded JWT token.

    Raises:
        ValueError: If there is an issue with token creation.
    """
    try:
        # Create a copy of the data dictionary to avoid modifying the original input.
        to_encode = data.copy()

        # Calculate the expiration time by adding the specified duration to the current UTC time.
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)

        # Add the expiration time as the "exp" field in the token payload.
        to_encode.update({"exp": expire})

        # Encode the payload into a JWT string using the SECRET_KEY and the specified ALGORITHM.
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        # Return the successfully created JWT.
        return encoded_jwt

    except JWTError as e:
        # Handle exceptions related to the JWT encoding process.
        raise ValueError(f"An error occurred while creating the access token: {e}")

    except Exception as e:
        # Handle any other unexpected exceptions and re-raise them with a custom message.
        raise ValueError(f"Unexpected error during token creation: {e}")



def verify_token(token: str):
    """
    Verify a JWT token and decode its payload.

    Args:
        token (str): The JWT token to verify.

    Returns:
        dict: The decoded payload if the token is valid.
        None: If the token is invalid or verification fails.
    """
    try:
        # Decode the token using the secret key and the specified algorithm.
        # If the token is invalid, jwt.decode raises an exception.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Return the decoded payload if verification is successful.
    except JWTError as jwt_error:
        # Handle JWT-specific errors (e.g., invalid signature, expired token).
        print(f"JWT Error: {jwt_error}")  # Log the error for debugging purposes.
        return None  # Return None to indicate verification failure.
    except Exception as general_error:
        # Handle any other unexpected errors for robustness.
        print(f"Unexpected Error during token verification: {general_error}")
        return None
