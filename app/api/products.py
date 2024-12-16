from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.products import ProductCreate, ProductUpdate, ProductResponse
from core.auth import get_db, get_current_user, is_admin, is_vendor
from crud.products import (
    create_product_in_db,
    get_all_products_from_db,
    get_product_by_id_from_db,
    update_product_in_db,
    delete_product_from_db,
)
from typing import List
from uuid import UUID

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.post("/", response_model=ProductResponse, dependencies=[Depends(is_vendor)])
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a new product.

    - **product**: The ProductCreate schema containing the product's details.
    - **db**: Database session dependency for database interaction.
    - **current_user**: The currently authenticated user.
    - **Depends(is_vendor)**: Ensures only vendors can access this endpoint.
    - The `current_user.vendor_id` is used to associate the product with the vendor.
    - Returns the created product using the ProductResponse schema.
    """
    return await create_product_in_db(db, product, current_user.vendor_id)

# get all products
@router.get("/", response_model=List[ProductResponse])
async def get_all_products(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all products.

    - **db**: Database session dependency for database interaction.
    - Returns a list of products using the ProductResponse schema.
    """
    return await get_all_products_from_db(db)

# get product
@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a product by its ID.

    - **product_id**: UUID of the product to retrieve.
    - **db**: Database session dependency for database interaction.
    - Returns the product details using the ProductResponse schema.
    """
    return await get_product_by_id_from_db(db, product_id)

# update product
@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_update: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update an existing product.

    - **product_id**: UUID of the product to update.
    - **product_update**: ProductUpdate schema containing the updated product details.
    - **db**: Database session dependency for database interaction.
    - **current_user**: The currently authenticated user.
    - Ensures that the current user is authorized to update the product.
    - Returns the updated product details using the ProductResponse schema.
    """
    return await update_product_in_db(db, product_id, product_update, current_user)

# delete product
@router.delete("/{product_id}", dependencies=[Depends(is_vendor)])
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Delete a product.

    - **product_id**: UUID of the product to delete.
    - **db**: Database session dependency for database interaction.
    - **current_user**: The currently authenticated user.
    - **Depends(is_vendor)**: Ensures only vendors can access this endpoint.
    - Ensures that the product belongs to the current user before deletion.
    - Returns a success message upon successful deletion.
    """
    await delete_product_from_db(db, product_id, current_user)
    return {"message": "Product deleted successfully"}
