from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models.orders import Order, OrderItem
from schemas.orders import OrderCreate
from fastapi import HTTPException, status

## create new order
async def create_order(db: AsyncSession, order_data: OrderCreate):
    """
    Create a new order in the database.

    - **db**: The database session for performing database operations.
    - **order_data**: An OrderCreate schema containing the details of the order.
    - Steps:
        1. Create and save the order with basic information (user, total amount, status, shipping address).
        2. Add associated order items to the order.
    - Commits the transaction after saving the order and its items.
    - Returns the newly created order.
    """
    # Create the Order
    new_order = Order(
        user_id=order_data.user_id,  # User who placed the order
        total_amount=order_data.total_amount,  # Total cost of the order
        status=order_data.status,  # Current status of the order
        shipping_address=order_data.shipping_address  # Shipping address for the order
    )
    db.add(new_order)  # Add the order to the database session
    await db.commit()  # Commit the order to the database
    await db.refresh(new_order)  # Refresh the order instance to get the latest data

    # Add Order Items
    for item in order_data.order_items:  # Iterate over the provided order items
        order_item = OrderItem(
            order_id=new_order.order_id,  # Associate the item with the newly created order
            product_id=item.product_id,  # ID of the product
            quantity=item.quantity,  # Quantity of the product ordered
            price=item.price  # Price per unit of the product
        )
        db.add(order_item)  # Add the order item to the database session

    await db.commit()  # Commit the order items to the database
    return new_order  # Return the created order


async def get_all_orders(db: AsyncSession, status: str = None):
    """
    Retrieve all orders, optionally filtered by status.

    - **db**: The database session for performing database operations.
    - **status**: (Optional) Filter orders by their status (e.g., 'pending', 'shipped').
    - Executes a query to fetch orders from the database.
    - Returns a list of orders matching the criteria.
    """
    query = select(Order)  # Base query to select all orders
    if status:  # Add a filter if a specific status is provided
        query = query.filter(Order.status == status)

    result = await db.execute(query)  # Execute the query
    return result.scalars().all()  # Retrieve and return all matching orders


async def get_order_by_id(db: AsyncSession, order_id: str):
    """
    Retrieve an order by its ID.

    - **db**: The database session for performing database operations.
    - **order_id**: The unique identifier of the order.
    - Executes a query to fetch the order by its ID.
    - Raises a 404 HTTPException if the order is not found.
    - Returns the order if found.
    """
    result = await db.execute(select(Order).filter(Order.order_id == order_id))  # Query for the order by ID
    order = result.scalars().first()  # Retrieve the first result

    if not order:  # Check if the order exists
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return order  # Return the order


async def update_order(db: AsyncSession, order_id: str, status: str = None, cancellation_reason: str = None):
    """
    Update an order's status or cancellation reason.

    - **db**: The database session for performing database operations.
    - **order_id**: The unique identifier of the order.
    - **status**: (Optional) The new status to update the order to.
    - **cancellation_reason**: (Optional) The reason for canceling the order.
    - Checks if the order exists and raises a 404 HTTPException if not found.
    - Updates the provided fields and commits the changes.
    - Returns the updated order.
    """
    result = await db.execute(select(Order).filter(Order.order_id == order_id))  # Query for the order by ID
    order = result.scalars().first()  # Retrieve the first result

    if not order:  # Check if the order exists
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    # Update the order status if provided
    if status:
        order.status = status
    # Update the cancellation reason if provided
    if cancellation_reason:
        order.cancellation_reason = cancellation_reason

    await db.commit()  # Commit the changes to the database
    await db.refresh(order)  # Refresh the order instance to get the updated data
    return order  # Return the updated order


async def delete_order(db: AsyncSession, order_id: str):
    """
    Delete an order and its associated items.

    - **db**: The database session for performing database operations.
    - **order_id**: The unique identifier of the order.
    - Checks if the order exists and raises a 404 HTTPException if not found.
    - Deletes the order and commits the transaction.
    - Returns a success message upon deletion.
    """
    result = await db.execute(select(Order).filter(Order.order_id == order_id))  # Query for the order by ID
    order = result.scalars().first()  # Retrieve the first result

    if not order:  # Check if the order exists
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    # Delete the order
    await db.delete(order)  # Delete the order from the database session
    await db.commit()  # Commit the changes to the database
    return {"message": "Order deleted successfully"}  # Return a success message


