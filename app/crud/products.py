from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from models import Product
from schemas import ProductCreate, ProductUpdate
from uuid import UUID
from fastapi import HTTPException, status

async def create_product_in_db(db: AsyncSession, product_data: ProductCreate, vendor_id: UUID) -> Product:
    """Create a new product in the database."""
    new_product = Product(**product_data.dict(), vendor_id=vendor_id)
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product

async def get_all_products_from_db(db: AsyncSession):
    """Retrieve all products."""
    result = await db.execute(select(Product))
    return result.scalars().all()

async def get_product_by_id_from_db(db: AsyncSession, product_id: UUID) -> Product:
    """Retrieve a product by its ID."""
    product = await db.execute(select(Product).filter(Product.product_id == product_id))
    product = product.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

async def update_product_in_db(db: AsyncSession, product_id: UUID, product_update: ProductUpdate, current_user) -> Product:
    """Update a product."""
    product = await db.execute(select(Product).filter(Product.product_id == product_id))
    product = product.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Ensure only the vendor who created the product or an admin can update it
    if current_user.role != "admin" and current_user.vendor_id != product.vendor_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this product")

    for key, value in product_update.dict(exclude_unset=True).items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)
    return product

async def delete_product_from_db(db: AsyncSession, product_id: UUID, current_user) -> None:
    """Delete a product."""
    product = await db.execute(select(Product).filter(Product.product_id == product_id))
    product = product.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Ensure only the vendor who created the product or an admin can delete it
    if current_user.role != "admin" and current_user.vendor_id != product.vendor_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this product")

    await db.delete(product)
    await db.commit()
