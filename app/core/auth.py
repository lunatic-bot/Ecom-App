# auth.py
from passlib.context import CryptContext  # type: ignore # Importing password encryption library
from fastapi import Depends, HTTPException, status  # Importing FastAPI dependencies for handling HTTP exceptions and status codes
from starlette.requests import Request  # Importing Request object for managing HTTP requests
from sqlalchemy.orm import Session  # Importing SQLAlchemy session for interacting with the database
from datetime import datetime, timedelta, timezone
# from pytz import timezone  # Importing timezone utilities for time zone handling
from jose import JWTError, jwt  # type: ignore # Importing JWT (JSON Web Token) utilities for token creation and verification
from fastapi.security import OAuth2PasswordBearer  # Importing OAuth2PasswordBearer for token authentication
from sqlalchemy.future import select


from db.database import get_db  # Importing database dependency for session management
from db.models.user import User  # Importing the User model from the database models
from sqlalchemy.ext.asyncio import AsyncSession


# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Password hashing context setup using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "57168498522b9b42531f34be15dcd8d7e1a5fe14261c7d80e82cb9cdac26bd6b"  # Secret key used for signing JWTs
ALGORITHM = "HS256"  # Algorithm used for encoding JWTs
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Access token expiration time in minutes

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if the plain password matches the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Fetch user from the database
    result = await db.execute(select(User).filter(User.user_id == int(user_id)))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user



# Function to get the current user from the access token stored in cookies
# def get_current_user(request: Request, db: Session = Depends(get_db)):
#     """Retrieve the current user from the JWT token stored in cookies."""
#     print("GET CURRENT USER : ")
    
#     # Define the exception to raise in case of invalid credentials
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
    
#     try:
#         # Retrieve the token from the cookies
#         token = request.cookies.get("access_token")
        
#         # Remove "Bearer " prefix from token if it exists
#         if token:
#             token = token.replace("Bearer ", "")
#         else:
#             raise credentials_exception
        
#         print("Token from cookie:", token)
        
#         # Decode the JWT using the secret key and the algorithm
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         print("Payload:", payload)
        
#         # Extract the username (email) from the JWT payload
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
        
#         # Query the database to find the user based on the email
#         user = db.query(User).filter(User.email == username).first()
#         if user is None:
#             raise credentials_exception
        
#         # Return the user object if found
#         return user
#     except JWTError:
#         # Raise an exception if there is an error decoding the JWT
#         raise credentials_exception

# # Function to create an access token (JWT) with an optional expiration time
# def create_access_token(data: dict, expires_delta: timedelta = None):
#     """Create a JWT token for the user with expiration."""
#     to_encode = data.copy()  # Copy the data to avoid modifying the original input
    
#     # Set the token's expiration time
#     if expires_delta:
#         expire = datetime.now(timezone("Asia/Kolkata")) + expires_delta
#     else:
#         expire = datetime.now(timezone("Asia/Kolkata")) + timedelta(minutes=15)
    
#     # Add the expiration time to the token's payload
#     to_encode.update({"exp": expire})
    
#     # Encode the JWT using the secret key and algorithm
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
#     # Return the encoded JWT
#     return encoded_jwt



def create_access_token(data: dict, expires_in_minutes: int):
    """
    Create a JWT token with a specified expiration time.

    Args:
        data (dict): Payload data for the token.
        expires_in_minutes (int): Token expiration time in minutes.

    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt





def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as jt:
        print(jt)
        return None

