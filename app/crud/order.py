from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models.order import Order, OrderItem
from schemas.order import OrderCreate, OrderItemCreate
from fastapi import HTTPException, status
from datetime import datetime

## create new order
async def create_order(db: AsyncSession, order_data: OrderCreate):
    # Create the Order
    new_order = Order(
        user_id=order_data.user_id,
        total_amount=order_data.total_amount,
        status=order_data.status,
        shipping_address=order_data.shipping_address
    )
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)

    # Add Order Items
    for item in order_data.order_items:
        order_item = OrderItem(
            order_id=new_order.order_id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price
        )
        db.add(order_item)

    await db.commit()
    return new_order


async def get_all_orders(db: AsyncSession, status: str = None):
    query = select(Order)
    if status:
        query = query.filter(Order.status == status)

    result = await db.execute(query)
    return result.scalars().all()


async def get_order_by_id(db: AsyncSession, order_id: str):
    result = await db.execute(select(Order).filter(Order.order_id == order_id))
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return order


async def update_order(db: AsyncSession, order_id: str, status: str = None, cancellation_reason: str = None):
    result = await db.execute(select(Order).filter(Order.order_id == order_id))
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if status:
        order.status = status
    if cancellation_reason:
        order.cancellation_reason = cancellation_reason

    await db.commit()
    await db.refresh(order)
    return order


async def delete_order(db: AsyncSession, order_id: str):
    result = await db.execute(select(Order).filter(Order.order_id == order_id))
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    # Delete the order and its items
    await db.delete(order)
    await db.commit()
    return {"message": "Order deleted successfully"}


