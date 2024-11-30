from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from uuid import UUID

class OrderItemBase(BaseModel):
    product_id: UUID
    quantity: int
    price: Decimal

class OrderItemCreate(OrderItemBase):
    pass

class OrderBase(BaseModel):
    user_id: int
    total_amount: Decimal
    shipping_address: str

class OrderCreate(OrderBase):
    order_items: List[OrderItemCreate]

class OrderResponse(OrderBase):
    order_id: UUID
    status: str
    order_items: List[OrderItemBase]

    class Config:
        orm_mode = True
