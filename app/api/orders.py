from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from schemas.orders import OrderCreate, OrderResponse
from crud.orders import create_order, get_all_orders, get_order_by_id, update_order, delete_order
from typing import List

router = APIRouter()

## Endpoint to create a new order
@router.post("/orders", response_model=OrderResponse, tags=["Order"])
async def create_new_order(order_data: OrderCreate, db: AsyncSession = Depends(get_db)):
    # Accepts order data in the form of an OrderCreate schema
    # Establishes a database connection using dependency injection
    # Calls the create_order function to save the order to the database and return the created order
    return await create_order(db, order_data)

## Endpoint to list all orders
@router.get("/orders", response_model=List[OrderResponse], tags=["Order"])
async def list_all_orders(status: str = None, db: AsyncSession = Depends(get_db)):
    # Optionally filters orders by their status if the 'status' query parameter is provided
    # Establishes a database connection using dependency injection
    # Calls the get_all_orders function to retrieve and return a list of orders
    return await get_all_orders(db, status)

## Endpoint to retrieve a specific order by its ID
@router.get("/orders/{order_id}", response_model=OrderResponse, tags=["Order"])
async def retrieve_order(order_id: str, db: AsyncSession = Depends(get_db)):
    # Accepts the order ID as a path parameter
    # Establishes a database connection using dependency injection
    # Calls the get_order_by_id function to fetch and return the order with the given ID
    return await get_order_by_id(db, order_id)

## Endpoint to update an order
@router.put("/orders/{order_id}", response_model=OrderResponse, tags=["Order"])
async def modify_order(order_id: str, status: str = None, cancellation_reason: str = None, db: AsyncSession = Depends(get_db)):
    # Accepts the order ID as a path parameter
    # Optionally accepts a new status and a cancellation reason as query parameters
    # Establishes a database connection using dependency injection
    # Calls the update_order function to update the specified order and return the updated order details
    return await update_order(db, order_id, status, cancellation_reason)

## Endpoint to delete an order
@router.delete("/orders/{order_id}", tags=["Order"])
async def remove_order(order_id: str, db: AsyncSession = Depends(get_db)):
    # Accepts the order ID as a path parameter
    # Establishes a database connection using dependency injection
    # Calls the delete_order function to remove the specified order from the database
    # Returns the outcome of the deletion operation
    return await delete_order(db, order_id)