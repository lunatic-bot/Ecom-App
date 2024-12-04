from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models import Product
from schemas import ProductCreate, ProductUpdate, ProductResponse
from dependencies import get_db, get_current_user, is_admin, is_vendor

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.post("/", response_model=ProductResponse, dependencies=[Depends(is_vendor)])
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    # Only vendors can create products
    new_product = Product(**product.dict(), vendor_id=current_user.vendor_id)
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product

@router.get("/", response_model=List[ProductResponse])
async def get_all_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: UUID, db: AsyncSession = Depends(get_db)):
    product = await db.execute(select(Product).filter(Product.product_id == product_id))
    product = product.scalars().first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_update: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
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

@router.delete("/{product_id}", dependencies=[Depends(is_vendor)])
async def delete_product(product_id: UUID, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    product = await db.execute(select(Product).filter(Product.product_id == product_id))
    product = product.scalars().first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Ensure only the vendor who created the product or an admin can delete it
    if current_user.role != "admin" and current_user.vendor_id != product.vendor_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this product")

    await db.delete(product)
    await db.commit()
    return {"message": "Product deleted successfully"}

