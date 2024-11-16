# Importing necessary modules from FastAPI, SQLAlchemy, Starlette, and other packages
from fastapi import Depends, HTTPException, status, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.users import UserResponse, Token  # Pydantic models for user response and token
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request  # Handling HTTP requests
from fastapi.security import OAuth2PasswordRequestForm  # OAuth2 form for login
from datetime import datetime, timedelta  # Handling date and time operations
from pytz import timezone  # Managing time zones
from email_validator import validate_email, EmailNotValidError  # Validating email addresses

# Importing CRUD operations, templates, database utilities, authentication methods, and utility functions
import app.crud.users as crud
from app.db.database import get_db
from app.core.auth import create_access_token, get_current_user, get_password_hash
from app.utlis.utils import generate_reset_token, send_email
from app.db.models.user import User  # User model

# Defining an API router for managing user routes
from fastapi import APIRouter
router = APIRouter()

# Token expiration time for access tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Route to handle user signup (POST method)
@router.post("/users/register", response_model=UserResponse)
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
    await send_email("Welcome", username, email)

    return {"status" : "success", "user": new_user}    


  


# Route to handle login and issue access tokens (POST method)
@router.post("/token", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),  # Collecting OAuth2 form data for login
    db: AsyncSession = Depends(get_db)  # Injecting database session
):
    # Authenticate the user using the provided username and password
    user = await crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # If authentication fails, return the login page with an error message
        error_message = "Incorrect username or password"
        return {"request": request, "message": error_message, "message_type": "danger"}
    
    # Create an access token that expires after a set time
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}




# Route to request a password reset (POST method)
@router.post("/users/request-password-reset")
async def request_password_reset(
    email: str = Form(...),  # Collect email from form
    db: AsyncSession = Depends(get_db)  # Inject database session
):
    # Validate the email format
    try:
        email = validate_email(email).email
    except EmailNotValidError:
        # If invalid, raise an HTTP exception with a 400 status
        raise HTTPException(
            status_code=400,
            detail="Invalid email address. Please enter a valid email."
        )

    # Check if the user exists
    db_user = await crud.get_user_by_mail(db, email)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="Email not found. Please check the email address you entered."
        )

    # Generate a reset token and save it with the expiration time
    token = generate_reset_token()
    expiration_time = datetime.now(timezone("Asia/Kolkata")) + timedelta(minutes=30)
    db_user.reset_token = token
    db_user.reset_token_expiration = expiration_time
    db.commit()

    # Send the password reset email with the reset link
    reset_link = f"http://localhost:8000/reset-password?token={token}"
    await send_email("Password_reset", db_user.username, db_user.email, reset_link)

    # Return a JSON response confirming that the reset email was sent
    return {"message": "Password reset email has been sent.", "email": email}




# Route to handle password reset (POST method)
@router.post("/users/reset-password/")
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
