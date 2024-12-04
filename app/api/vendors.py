from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models import Vendor
from schemas import VendorCreate, VendorUpdate, VendorResponse
from dependencies import get_db, get_current_user, is_superuser

router = APIRouter(
    prefix="/vendors",
    tags=["Vendors"]
)

# Create Vendor (Admin Only)
@router.post("/", response_model=VendorResponse, dependencies=[Depends(is_superuser)])
async def create_vendor(vendor: VendorCreate, db: AsyncSession = Depends(get_db)):
    # Check if the email already exists
    existing_vendor = await db.execute(select(Vendor).filter(Vendor.email == vendor.email))
    if existing_vendor.scalars().first():
        raise HTTPException(status_code=400, detail="Vendor with this email already exists")

    # Create the vendor
    new_vendor = Vendor(**vendor.dict())
    db.add(new_vendor)
    await db.commit()
    await db.refresh(new_vendor)
    return new_vendor

# Get All Vendors (Admin Only)
@router.get("/", response_model=List[VendorResponse], dependencies=[Depends(is_superuser)])
async def get_all_vendors(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vendor))
    vendors = result.scalars().all()
    return vendors

# Get Vendor by ID (Vendor/Admin)
@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(vendor_id: UUID, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    vendor = await db.execute(select(Vendor).filter(Vendor.vendor_id == vendor_id))
    vendor = vendor.scalars().first()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Ensure the current user is the vendor or an admin
    if current_user.role != "admin" and current_user.vendor_id != vendor_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this vendor")

    return vendor

# Update Vendor (Vendor Only)
@router.put("/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    vendor_id: UUID,
    vendor_update: VendorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    vendor = await db.execute(select(Vendor).filter(Vendor.vendor_id == vendor_id))
    vendor = vendor.scalars().first()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Ensure only the vendor themselves can update their details
    if current_user.vendor_id != vendor_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this vendor")

    for key, value in vendor_update.dict(exclude_unset=True).items():
        setattr(vendor, key, value)

    await db.commit()
    await db.refresh(vendor)
    return vendor

# Delete Vendor (Admin Only)
@router.delete("/{vendor_id}", dependencies=[Depends(is_superuser)])
async def delete_vendor(vendor_id: UUID, db: AsyncSession = Depends(get_db)):
    vendor = await db.execute(select(Vendor).filter(Vendor.vendor_id == vendor_id))
    vendor = vendor.scalars().first()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    await db.delete(vendor)
    await db.commit()
    return {"message": "Vendor deleted successfully"}


