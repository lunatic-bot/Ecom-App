# Import Pydantic's BaseModel and EmailStr for validation
from pydantic import BaseModel, EmailStr  
# Import Optional for nullable fields, and List for list types
from typing import Optional, List
# Import datetime for time-related fields  
from datetime import datetime  


# Schema for user creation, used during sign-up
class UserCreate(BaseModel):
    username: str  
    email: EmailStr  
    password: str  

# Schema for user response after successful sign-up or retrieval
class UserResponse(BaseModel):
    id: int  
    username: str  
    email: EmailStr  
    creation_time: datetime  
    class Config:
        orm_mode = True  

# Schema for the login response, containing the JWT access token
class Token(BaseModel):
    access_token: str  # The JWT token for authentication
    token_type: str  # Type of the token, typically "Bearer"

# Schema for requesting a password reset
class ResetRequest(BaseModel):
    email: str  

# Schema for resetting the password using a reset token
class PasswordResetForm(BaseModel):
    token: str  # The token sent to the user's email for password reset, required
    new_password: str  
    confirm_password: str  
