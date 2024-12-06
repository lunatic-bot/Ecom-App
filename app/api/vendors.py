from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import VendorCreate, VendorUpdate, VendorResponse
from dependencies import get_db, is_admin
from crud.vendors import (
    create_vendor_in_db,
    get_all_vendors_from_db,
    get_vendor_by_id_from_db,
    update_vendor_in_db,
    delete_vendor_from_db,
)
from typing import List
from uuid import UUID

router = APIRouter(
    prefix="/vendors",
    tags=["Vendors"],
)

@router.post("/", response_model=VendorResponse, dependencies=[Depends(is_admin)])
async def create_vendor(vendor: VendorCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new vendor.

    - **vendor**: The VendorCreate schema containing the vendor's details.
    - **db**: Database session dependency for database interaction.
    - **Depends(is_admin)**: Ensures only admin users can access this endpoint.
    """
    return await create_vendor_in_db(db, vendor)


@router.get("/", response_model=List[VendorResponse])
async def get_all_vendors(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all vendors.

    - **db**: Database session dependency for database interaction.
    - Returns a list of vendors using the VendorResponse schema.
    """
    return await get_all_vendors_from_db(db)


@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(vendor_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a vendor by its ID.

    - **vendor_id**: UUID of the vendor to retrieve.
    - **db**: Database session dependency for database interaction.
    - Returns the vendor details using the VendorResponse schema.
    """
    return await get_vendor_by_id_from_db(db, vendor_id)


@router.put("/{vendor_id}", response_model=VendorResponse, dependencies=[Depends(is_admin)])
async def update_vendor(
    vendor_id: UUID, vendor_update: VendorUpdate, db: AsyncSession = Depends(get_db)
):
    """
    Update vendor details.

    - **vendor_id**: UUID of the vendor to update.
    - **vendor_update**: VendorUpdate schema containing updated vendor details.
    - **db**: Database session dependency for database interaction.
    - **Depends(is_admin)**: Ensures only admin users can access this endpoint.
    - Returns the updated vendor details using the VendorResponse schema.
    """
    return await update_vendor_in_db(db, vendor_id, vendor_update)


@router.delete("/{vendor_id}", dependencies=[Depends(is_admin)])
async def delete_vendor(vendor_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Delete a vendor.

    - **vendor_id**: UUID of the vendor to delete.
    - **db**: Database session dependency for database interaction.
    - **Depends(is_admin)**: Ensures only admin users can access this endpoint.
    - Returns a success message upon successful deletion.
    """
    await delete_vendor_from_db(db, vendor_id)
    return {"message": "Vendor deleted successfully"}
