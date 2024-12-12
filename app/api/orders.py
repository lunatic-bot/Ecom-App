from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from schemas.orders import OrderCreate, OrderResponse
from crud.orders import create_order, get_all_orders, get_order_by_id, update_order, delete_order
from typing import List

router = APIRouter()

## create new order
@router.post("/orders", response_model=OrderResponse, tags=["Order"])
async def create_new_order(order_data: OrderCreate, db: AsyncSession = Depends(get_db)):
    return await create_order(db, order_data)

@router.get("/orders", response_model=List[OrderResponse], tags=["Order"])
async def list_all_orders(status: str = None, db: AsyncSession = Depends(get_db)):
    return await get_all_orders(db, status)

@router.get("/orders/{order_id}", response_model=OrderResponse, tags=["Order"])
async def retrieve_order(order_id: str, db: AsyncSession = Depends(get_db)):
    return await get_order_by_id(db, order_id)

@router.put("/orders/{order_id}", response_model=OrderResponse, tags=["Order"])
async def modify_order(order_id: str, status: str = None, cancellation_reason: str = None, db: AsyncSession = Depends(get_db)):
    return await update_order(db, order_id, status, cancellation_reason)

@router.delete("/orders/{order_id}", tags=["Order"])
async def remove_order(order_id: str, db: AsyncSession = Depends(get_db)):
    return await delete_order(db, order_id)

