# Importing necessary modules from FastAPI, SQLAlchemy, Starlette, and other packages
from fastapi import Depends, HTTPException, status, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request  # Handling HTTP requests
from fastapi.security import OAuth2PasswordRequestForm  # OAuth2 form for login
from datetime import datetime, timedelta, timezone  # Handling date and time operations
from email_validator import validate_email, EmailNotValidError  # Validating email addresses
from sqlalchemy.future import select

# Importing CRUD operations, templates, database utilities, authentication methods, and utility functions
import crud.users as crud
from db.database import get_db
from core.auth import create_access_token, get_current_user, get_password_hash, verify_token
from utlis.utils import generate_reset_token, send_email
from app.db.models.users import User  # User model
from schemas.users import UserResponse, Token, TokenResponse, UserUpdate # Pydantic models for user response and token

# Defining an API router for managing user routes
from fastapi import APIRouter
router = APIRouter()

# Token expiration time for access tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 1440


# Route to handle user signup (POST method)
@router.post("/users/register", response_model=UserResponse, tags=["User"])
async def create_user(
    username: str = Form(...),  # Collecting username from form data
    email: str = Form(...),  # Collecting email from form data
    password: str = Form(...),  # Collecting password from form data
    confirm_password: str = Form(...),  # Collecting confirmation password
    db: AsyncSession = Depends(get_db)  # Injecting database session dependency
):
    # If the passwords do not match, raise an HTTP 400 error
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Check if a user with the provided email already exists
    # db_user = db.query(User).filter(User.email == email).first()
    db_user = await crud.get_user_by_mail(db, email)
    print(db_user)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create a new user in the database using the CRUD function
    new_user = await crud.create_user_in_db(db, username, email, password)
    
    # Send a welcome email after successful signup
    # await send_email("Welcome", username, email)
    return new_user    


@router.put("/users/{user_id}", response_model=UserResponse, tags=["Admin"])
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update user information.

    Args:
        user_id (int): The ID of the user to be updated.
        user_update (UserUpdate): The updated user data sent in the request body.
        db (AsyncSession): Database session dependency for querying and updating the user.
        current_user (User): The currently authenticated user, determined from the JWT token.

    Returns:
        UserResponse: The updated user object.

    Raises:
        HTTPException: 
            - 403 Forbidden if the current user is not authorized to update the user.
            - 404 Not Found if the user to be updated does not exist.
    """
    # Check if the current user is authorized to perform the update.
    # Only admins or the user themselves can update their profile.
    if current_user.role != "admin" and current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    # Call a function to update the user in the database.
    # This function is typically part of a CRUD (Create, Read, Update, Delete) module.
    user = await crud.update_user(db, user_id, user_update)

    # Return the updated user object.
    return user


@router.get("/users", response_model=list[UserResponse], tags=["Admin"])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a list of all users.

    Args:
        db (AsyncSession): Database session dependency for querying users.
        current_user (User): The currently authenticated user, determined from the JWT token.

    Returns:
        list[UserResponse]: A list of all users in the database.

    Raises:
        HTTPException:
            - 403 Forbidden if the current user is not an admin.
    """
    # Authorization check to ensure only admins can access this endpoint.
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )

    # Fetch all users from the database using a CRUD function.
    users = await crud.get_all_users(db)

    # Return the list of users.
    return users


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Admin"])
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a user by their ID.

    Args:
        user_id (int): The ID of the user to be deleted.
        db (AsyncSession): Database session dependency for querying and deleting users.
        current_user (User): The currently authenticated user, determined from the JWT token.

    Returns:
        None: Indicates successful deletion with a 204 No Content status.

    Raises:
        HTTPException:
            - 403 Forbidden if the current user is not an admin.
            - 404 Not Found if the user to be deleted does not exist.
    """
    # Authorization check to ensure only admins can delete users.
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete users"
        )

    # Attempt to delete the user by calling the CRUD function.
    # If the user doesn't exist, the CRUD function should raise an appropriate exception.
    user = await crud.delete_user(db, user_id=user_id)

    # Return None to signify successful deletion with a 204 No Content response.
    return user


@router.post("/token", response_model=Token, tags=["User"])
async def login_for_access_and_refresh_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),  # Dependency to parse OAuth2 form data (username and password)
    db: AsyncSession = Depends(get_db),  # Dependency to provide an async database session
):
    """
    Endpoint to authenticate a user and issue both access and refresh tokens.

    Args:
        request (Request): FastAPI request object for handling the request context.
        form_data (OAuth2PasswordRequestForm): Form data containing the username and password.
        db (AsyncSession): Database session for querying the user table.

    Returns:
        dict: A dictionary containing the access token, refresh token, and token type.

    Raises:
        HTTPException: 
            - 401 Unauthorized if authentication fails.
    """
    # Authenticate the user using the provided credentials
    user = await crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # If authentication fails, raise an HTTP 401 Unauthorized error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate the access token with a specified expiration time
    access_token = create_access_token(
        data={"sub": str(user.user_id), "email": user.email, "role": str(user.role)},
        expires_in_minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Generate the refresh token with a longer expiration time
    refresh_token = create_access_token(
        data={"sub": str(user.user_id), "email": user.email, "role": str(user.role)},
        expires_in_minutes=REFRESH_TOKEN_EXPIRE_MINUTES
    )

    # Save the refresh token in the database
    saved_token = await crud.save_refresh_token(db, refresh_token, user.user_id, REFRESH_TOKEN_EXPIRE_MINUTES)

    # Return the tokens to the user
    return {
        "access_token": access_token,  # Short-lived token for accessing secure resources
        "refresh_token": refresh_token,  # Long-lived token for obtaining new access tokens
        "token_type": "bearer"  # Token type (OAuth2 specification)
    }

@router.post("/refresh", response_model=TokenResponse, tags=["User"])
async def refresh_access_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to refresh an access token using a valid refresh token.

    Args:
        refresh_token (str): The refresh token provided by the client.
        db (AsyncSession): Asynchronous database session for querying token data.

    Returns:
        dict: A dictionary containing a new access token, the existing refresh token, and the token type.

    Raises:
        HTTPException:
            - 401 Unauthorized: If the refresh token is invalid or expired.
    """
    # Step 1: Verify the refresh token
    payload = verify_token(refresh_token)  # Decodes and validates the refresh token
    print(payload)  # Debugging purpose to check the payload structure

    if not payload:
        # Raise error if token verification fails
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Step 2: Extract user information from the token payload
    user_id = payload.get("sub")   # The user ID from the token
    user_email = payload.get("email")  # The user's email address
    user_role = payload.get("role")  # The user's role (e.g., admin, user)

    # Step 3: Check the refresh token against the database
    token_entry = await crud.get_token_for_user(db, refresh_token, user_id)

    # Verify if the token exists in the database and if it hasn't expired
    if not token_entry or token_entry.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )

    # Step 4: Generate a new access token
    access_token = create_access_token(
        data={"sub": str(user_id), "email": user_email, "role": user_role},
        expires_in_minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Step 5: Return the new access token and existing refresh token
    return {
        "access_token": access_token,  # New access token for authentication
        "refresh_token": refresh_token,  # Existing refresh token (still valid)
        "token_type": "bearer"  # Token type as per OAuth2 standards
    }


# Route to request a password reset (POST method)
@router.post("/users/request-password-reset", tags=["User"])
async def request_password_reset(
    email: str = Form(...),  # Collect email from the form input
    db: AsyncSession = Depends(get_db)  # Inject an asynchronous database session
):
    """
    Handles password reset requests by generating a reset token and sending an email with a reset link.

    Args:
        email (str): The email address provided by the user.
        db (AsyncSession): The database session used to query and update user information.

    Returns:
        dict: A JSON response confirming the password reset email was sent.

    Raises:
        HTTPException:
            - 400 Bad Request: If the email is invalid.
            - 404 Not Found: If the email does not exist in the database.
    """
    # Step 1: Validate the provided email format
    try:
        email = validate_email(email).email  # Use a library to ensure the email is valid
    except EmailNotValidError:
        # Raise an exception if the email format is invalid
        raise HTTPException(
            status_code=400,
            detail="Invalid email address. Please enter a valid email."
        )

    # Step 2: Check if the user exists in the database
    db_user = await crud.get_user_by_mail(db, email)  # Query the user based on the email
    if not db_user:
        # Raise an exception if the email is not found in the database
        raise HTTPException(
            status_code=404,
            detail="Email not found. Please check the email address you entered."
        )

    # Step 3: Generate a reset token and set expiration
    token = generate_reset_token()  # Generate a unique token for the reset
    expiration_time = datetime.now(timezone("Asia/Kolkata")) + timedelta(minutes=30)  # Set token expiration time

    # Step 4: Save the reset token and expiration time in the database
    db_user.reset_token = token
    db_user.reset_token_expiration = expiration_time
    db.commit()  # Commit the changes to the database

    # Step 5: Send a password reset email with the reset link
    reset_link = f"http://localhost:8000/reset-password?token={token}"  # Construct the reset link
    await send_email("Password_reset", db_user.username, db_user.email, reset_link)  # Asynchronous email sending

    # Step 6: Return a success response to the user
    return {
        "message": "Password reset email has been sent.",  # Confirmation message
        "email": email  # Echo back the email for user verification
    }



# Route to handle password reset (POST method)
@router.post("/users/reset-password/", tags=["User"])
async def reset_password(
    token: str = Form(...),  # Collect reset token from form
    new_password: str = Form(...),  # Collect new password
    confirm_password: str = Form(...),  # Collect confirmation of the new password
    db: AsyncSession = Depends(get_db)  # Inject database session
):
    # Check if the new password matches the confirmation password
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Find the user by the reset token
    db_user = await crud.get_user_by_token(db, token)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # Hash the new password and update the user's data
    db_user.hashed_password = get_password_hash(new_password)
    db_user.reset_token = None  # Invalidate the token
    db_user.reset_token_expiration = None
    db.commit()

    # Send a confirmation email after the password is successfully reset
    login_link = f"http://localhost:8000/users/login"
    await send_email("Password_Changed", db_user.username, db_user.email, link=login_link)
    
    # Return a JSON response confirming the password reset
    return {"message": "Password has been successfully reset. You can now log in with your new password."}
