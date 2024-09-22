# Importing necessary modules from FastAPI, SQLAlchemy, Starlette, and other packages
from fastapi import Depends, HTTPException, status, Request, Form
from sqlalchemy.orm import Session
from app.schemas.schemas import UserResponse, Token  # Pydantic models for user response and token
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request  # Handling HTTP requests
from fastapi.security import OAuth2PasswordRequestForm  # OAuth2 form for login
from datetime import datetime, timedelta  # Handling date and time operations
from pytz import timezone  # Managing time zones
from email_validator import validate_email, EmailNotValidError  # Validating email addresses

# Importing CRUD operations, templates, database utilities, authentication methods, and utility functions
import app.crud.users as crud
from app.core.templates import templates
from app.db.database import get_db
from app.core.auth import create_access_token, get_current_user, get_password_hash
from app.utlis.utils import generate_reset_token, send_email
from app.models.users import User  # User model

# Defining an API router for managing user routes
from fastapi import APIRouter
router = APIRouter()

# Token expiration time for access tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Route to handle user signup (POST method)
@router.post("/users/signup", response_model=UserResponse)
async def create_user(
    username: str = Form(...),  # Collecting username from form data
    email: str = Form(...),  # Collecting email from form data
    password: str = Form(...),  # Collecting password from form data
    confirm_password: str = Form(...),  # Collecting confirmation password
    db: Session = Depends(get_db)  # Injecting database session dependency
):
    # If the passwords do not match, raise an HTTP 400 error
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Check if a user with the provided email already exists
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create a new user in the database using the CRUD function
    new_user = crud.create_user_in_db(db, username, email, password)
    
    # Send a welcome email after successful signup
    await send_email("Welcome", username, email)

    # Redirect the user to the login page after signup
    return RedirectResponse(url='/users/login', status_code=302)


# Route to serve the signup page (GET method)
@router.get('/users/signup')
def get_login_page(request: Request):
    # Return the signup template
    return templates.TemplateResponse("signup.html", {"request": request})    


# Route to handle login and issue access tokens (POST method)
@router.post("/token", response_model=Token)
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),  # Collecting OAuth2 form data for login
    db: Session = Depends(get_db)  # Injecting database session
):
    # Authenticate the user using the provided username and password
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # If authentication fails, return the login page with an error message
        error_message = "Incorrect username or password"
        return templates.TemplateResponse("login.html", {
            "request": request, "message": error_message, "message_type": "danger"
        })
    
    # Create an access token that expires after a set time
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    # Redirect to the todo page and set the access token in the user's cookie
    response = RedirectResponse(url='/read-todos', status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return response


# Route to serve the login page (GET method)
@router.get("/users/login")
def get_login_page(request: Request):
    # Fetch any message passed via query parameters (e.g., after a logout)
    message = request.query_params.get("message", "")
    # Return the login page template with the message, if any
    return templates.TemplateResponse("login.html", {"request": request, "message": message, "message_type": "info"})


# Route to handle user logout (GET method)
@router.get("/logout")
def logout(request: Request):
    # Redirect to the login page after logging out
    response = RedirectResponse(url='/users/login?message=You%20have%20been%20logged%20out')
    # Delete the access token from the user's cookie
    response.delete_cookie("access_token")
    return response


# # Route to read todos (GET method, same as previous one)
# @router.get("/", response_class=HTMLResponse)
# def read_todos(request: Request, skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
#     # Print the current user for debugging
#     print("Current user:", current_user)

#     # Redirect to the login page if not authenticated
#     if not current_user:
#         return RedirectResponse(url='/users/login?message=Please%20log%20in%20to%20continue', status_code=302)
    
#     # Fetch the user's todos with pagination
#     user = crud.get_user_by_mail(db, email=current_user.email)
#     todos, total_todos = crud.get_all_todos_for_user(db, skip, limit, user_id=user.id)
#     # Render the todos on the index page
#     return templates.TemplateResponse("index.html", {
#             "request": request,
#             "todos": todos,
#             "total": total_todos,
#             "skip": skip,
#             "limit": limit,
#             'current_user': current_user
#         })


# Route to request a password reset (POST method)
@router.post("/request-password-reset")
async def request_password_reset(
    request: Request,
    email: str = Form(...),  # Collect email from form
    db:Session = Depends(get_db)  # Inject database session
):
    # Validate the email format
    try:
        email = validate_email(email).email
    except EmailNotValidError:
        # If invalid, return the password reset form with an error message
        error_message = "Invalid email address. Please enter a valid email."
        return templates.TemplateResponse("request_password_reset.html", {"request": request, "error_message": error_message})

    # Check if the user exists
    db_user = crud.get_user_by_mail(db, email)
    if not db_user:
        error_message = "Email not found. Please check the email address you entered."
        return templates.TemplateResponse("request_password_reset.html", {"request": request, "error_message": error_message})

    # Generate a reset token and save it with the expiration time
    token = generate_reset_token()
    expiration_time = datetime.now(timezone("Asia/Kolkata")) + timedelta(minutes=30)
    db_user.reset_token = token
    db_user.reset_token_expiration = expiration_time
    db.commit()

    # Send the password reset email with the reset link
    reset_link = f"http://localhost:8000/reset-password?token={token}"
    await send_email("Password_reset", db_user.username, db_user.email, reset_link)
    
    # Render a response confirming that the reset email was sent
    return templates.TemplateResponse("password_reset_response.html", {"request": request})


# Route to serve the password reset request form (GET method)
@router.get("/request-password-reset", response_class=HTMLResponse)
async def request_password_reset_form(request: Request):
    # Return the password reset form template
    return templates.TemplateResponse("request_password_reset.html", {"request": request})


# Route to serve the password reset form (GET method)
@router.get("/reset-password/", response_class=HTMLResponse)
async def get_reset_password_form(token: str, request: Request):
    # Return the reset password form with the token
    return templates.TemplateResponse("reset_password.html", {"request": request, "token": token})


# Route to handle password reset (POST method)
@router.post("/reset-password/")
async def reset_password(
    request: Request,
    token: str = Form(...),  # Collect reset token from form
    new_password: str = Form(...),  # Collect new password
    confirm_password: str = Form(...),  # Collect confirmation of the new password
    db: Session = Depends(get_db)  # Inject database session
):
    # Check if the new password matches the confirmation password
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Find the user by the reset token
    db_user = crud.get_user_by_token(db, token)
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
    
    # Return a success template response
    return templates.TemplateResponse("password_reset_success.html", {"request": request})

