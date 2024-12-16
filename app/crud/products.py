from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models import Product
from schemas.products import ProductCreate, ProductUpdate
from uuid import UUID
from fastapi import HTTPException


async def create_product_in_db(db: AsyncSession, product_data: ProductCreate, vendor_id: UUID) -> Product:
    """
    Create a new product in the database.

    - **db**: The database session for performing database operations.
    - **product_data**: A ProductCreate schema containing the data for the new product.
    - **vendor_id**: The ID of the vendor creating the product.
    - Creates a new product instance, associates it with the vendor, and commits it to the database.
    - Refreshes the product instance to get the latest data from the database.
    - Returns the newly created product.
    """
    new_product = Product(**product_data.dict(), vendor_id=vendor_id)  # Create a new product and associate it with the vendor
    db.add(new_product)  # Add the product to the database session
    await db.commit()  # Commit the changes to the database
    await db.refresh(new_product)  # Refresh the instance to retrieve the latest data
    return new_product


async def get_all_products_from_db(db: AsyncSession):
    """
    Retrieve all products from the database.

    - **db**: The database session for performing database operations.
    - Executes a query to select all products from the database.
    - Returns a list of all products.
    """
    result = await db.execute(select(Product))  # Execute a query to select all products
    return result.scalars().all()  # Retrieve and return all product objects


async def get_product_by_id_from_db(db: AsyncSession, product_id: UUID) -> Product:
    """
    Retrieve a product by its ID.

    - **db**: The database session for performing database operations.
    - **product_id**: UUID of the product to retrieve.
    - Executes a query to select a product by its ID.
    - Raises a 404 HTTPException if the product is not found.
    - Returns the product if found.
    """
    product = await db.execute(select(Product).filter(Product.product_id == product_id))  # Query for the product by ID
    product = product.scalars().first()  # Retrieve the first result
    if not product:  # Check if the product exists
        raise HTTPException(status_code=404, detail="Product not found")
    return product


async def update_product_in_db(db: AsyncSession, product_id: UUID, product_update: ProductUpdate, current_user) -> Product:
    """
    Update a product's details in the database.

    - **db**: The database session for performing database operations.
    - **product_id**: UUID of the product to update.
    - **product_update**: ProductUpdate schema containing the updated data.
    - **current_user**: The currently logged-in user, used to check authorization.
    - Ensures that only the vendor who created the product or an admin can update it.
    - Updates the specified fields in the product and commits the changes.
    - Raises a 404 HTTPException if the product is not found.
    - Raises a 403 HTTPException if the user is not authorized to update the product.
    - Returns the updated product.
    """
    product = await db.execute(select(Product).filter(Product.product_id == product_id))  # Query for the product by ID
    product = product.scalars().first()  # Retrieve the first result
    if not product:  # Check if the product exists
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if the user is authorized to update the product
    if current_user.role != "admin" and current_user.vendor_id != product.vendor_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this product")

    # Update the product's attributes with the provided data
    for key, value in product_update.dict(exclude_unset=True).items():
        setattr(product, key, value)

    await db.commit()  # Commit the changes to the database
    await db.refresh(product)  # Refresh the product instance
    return product


async def delete_product_from_db(db: AsyncSession, product_id: UUID, current_user) -> None:
    """
    Delete a product from the database.

    - **db**: The database session for performing database operations.
    - **product_id**: UUID of the product to delete.
    - **current_user**: The currently logged-in user, used to check authorization.
    - Ensures that only the vendor who created the product or an admin can delete it.
    - Raises a 404 HTTPException if the product is not found.
    - Raises a 403 HTTPException if the user is not authorized to delete the product.
    - Deletes the product and commits the changes to the database.
    """
    product = await db.execute(select(Product).filter(Product.product_id == product_id))  # Query for the product by ID
    product = product.scalars().first()  # Retrieve the first result
    if not product:  # Check if the product exists
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if the user is authorized to delete the product
    if current_user.role != "admin" and current_user.vendor_id != product.vendor_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this product")

    await db.delete(product)  # Delete the product from the database
    await db.commit()  # Commit the changes
