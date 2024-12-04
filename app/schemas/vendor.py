from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class VendorCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: Optional[str]

class VendorUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    address: Optional[str]

class VendorResponse(BaseModel):
    vendor_id: UUID
    name: str
    email: EmailStr
    phone: str
    address: Optional[str]

    class Config:
        orm_mode = True
