from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class ProductCreate(BaseModel):
    name: str
    description: Optional[str]
    price: float
    stock: int

class ProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    stock: Optional[int]

class ProductResponse(BaseModel):
    product_id: UUID
    name: str
    description: Optional[str]
    price: float
    stock: int
    vendor_id: UUID

    class Config:
        orm_mode = True
