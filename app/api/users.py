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
from db.models.user import User  # User model
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
    # Check permissions
    if current_user.role != "admin" and current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user"
        )

    user = await crud.update_user(db, user_id, user_update)

    return user


@router.get("/users", response_model=list[UserResponse], tags=["Admin"])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this resource"
        )
    
    users = await crud.get_all_users(db)

    return users


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Admin"])
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete users"
        )

    user = await crud.delete_user(db, user_id=user_id)

    return user



@router.post("/token", response_model=Token, tags=["User"])
async def login_for_access_and_refresh_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),  # OAuth2 form data
    db: AsyncSession = Depends(get_db),  # Async database session
):
    # Authenticate the user
    user = await crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # Return error message if authentication fails
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate Access Token
    # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.user_id), "email":user.email, "role": str(user.role)}, expires_in_minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Generate Refresh Token
    # refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_access_token(data={"sub": str(user.user_id), "email":user.email, "role": str(user.role)}, expires_in_minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    saved_token = await crud.save_refresh_token(db, refresh_token, user.user_id, REFRESH_TOKEN_EXPIRE_MINUTES)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }



@router.post("/refresh", response_model=TokenResponse, tags=["User"])
async def refresh_access_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    # Verify refresh token
    payload = verify_token(refresh_token)
    print(payload)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("sub")
    user_email = payload.get("email")
    user_role = payload.get("role")
    # token_entry = db.query(Token).filter(Token.refresh_token == refresh_token, Token.user_id == user_id).first()
    # from sqlalchemy.future import select

    # Use an asynchronous query
    token_entry = await crud.get_token_for_user(db, refresh_token, user_id)

    if not token_entry or token_entry.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    # Generate new access token
    access_token = create_access_token({"sub": str(user_id), "email": user_email, "role": user_role}, expires_in_minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}



# Route to request a password reset (POST method)
@router.post("/users/request-password-reset", tags=["User"])
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
