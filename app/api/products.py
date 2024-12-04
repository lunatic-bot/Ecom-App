from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import ProductCreate, ProductUpdate, ProductResponse
from dependencies import get_db, get_current_user, is_admin, is_vendor
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
    return await create_product_in_db(db, product, current_user.vendor_id)

@router.get("/", response_model=List[ProductResponse])
async def get_all_products(db: AsyncSession = Depends(get_db)):
    return await get_all_products_from_db(db)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: UUID, db: AsyncSession = Depends(get_db)):
    return await get_product_by_id_from_db(db, product_id)

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_update: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await update_product_in_db(db, product_id, product_update, current_user)

@router.delete("/{product_id}", dependencies=[Depends(is_vendor)])
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await delete_product_from_db(db, product_id, current_user)
    return {"message": "Product deleted successfully"}

