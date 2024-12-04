from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from models import Vendor
from schemas import VendorCreate, VendorUpdate
from uuid import UUID
from fastapi import HTTPException, status

async def create_vendor_in_db(db: AsyncSession, vendor_data: VendorCreate) -> Vendor:
    """Create a new vendor in the database."""
    new_vendor = Vendor(**vendor_data.dict())
    db.add(new_vendor)
    await db.commit()
    await db.refresh(new_vendor)
    return new_vendor

async def get_all_vendors_from_db(db: AsyncSession):
    """Retrieve all vendors."""
    result = await db.execute(select(Vendor))
    return result.scalars().all()

async def get_vendor_by_id_from_db(db: AsyncSession, vendor_id: UUID) -> Vendor:
    """Retrieve a vendor by its ID."""
    vendor = await db.execute(select(Vendor).filter(Vendor.vendor_id == vendor_id))
    vendor = vendor.scalars().first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor

async def update_vendor_in_db(db: AsyncSession, vendor_id: UUID, vendor_update: VendorUpdate) -> Vendor:
    """Update vendor details."""
    vendor = await db.execute(select(Vendor).filter(Vendor.vendor_id == vendor_id))
    vendor = vendor.scalars().first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    for key, value in vendor_update.dict(exclude_unset=True).items():
        setattr(vendor, key, value)

    await db.commit()
    await db.refresh(vendor)
    return vendor

async def delete_vendor_from_db(db: AsyncSession, vendor_id: UUID) -> None:
    """Delete a vendor by its ID."""
    vendor = await db.execute(select(Vendor).filter(Vendor.vendor_id == vendor_id))
    vendor = vendor.scalars().first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    await db.delete(vendor)
    await db.commit()
