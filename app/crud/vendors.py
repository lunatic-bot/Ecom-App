from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from db.models import Vendor
from schemas.vendors import VendorCreate, VendorUpdate
from uuid import UUID
from fastapi import HTTPException, status

async def create_vendor_in_db(db: AsyncSession, vendor_data: VendorCreate) -> Vendor:
    """
    Create a new vendor in the database.

    - **db**: The database session for performing database operations.
    - **vendor_data**: A VendorCreate schema containing the data for the new vendor.
    - Creates a new vendor instance and commits it to the database.
    - Refreshes the instance to get the latest data from the database.
    - Returns the newly created vendor.
    """
    new_vendor = Vendor(**vendor_data.dict())  # Create a new vendor instance from the input data
    db.add(new_vendor)  # Add the vendor to the database session
    await db.commit()  # Commit the changes to the database
    await db.refresh(new_vendor)  # Refresh the instance to get updated data
    return new_vendor


async def get_all_vendors_from_db(db: AsyncSession):
    """
    Retrieve all vendors from the database.

    - **db**: The database session for performing database operations.
    - Executes a query to select all vendors.
    - Returns a list of all vendors.
    """
    result = await db.execute(select(Vendor))  # Execute a query to select all vendors
    return result.scalars().all()  # Retrieve all vendor objects


async def get_vendor_by_id_from_db(db: AsyncSession, vendor_id: UUID) -> Vendor:
    """
    Retrieve a vendor by its ID.

    - **db**: The database session for performing database operations.
    - **vendor_id**: UUID of the vendor to retrieve.
    - Executes a query to select a vendor by its ID.
    - Raises a 404 HTTPException if the vendor is not found.
    - Returns the vendor if found.
    """
    vendor = await db.execute(select(Vendor).filter(Vendor.vendor_id == vendor_id))  # Query for the vendor by ID
    vendor = vendor.scalars().first()  # Retrieve the first result
    if not vendor:  # Check if the vendor exists
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


async def update_vendor_in_db(db: AsyncSession, vendor_id: UUID, vendor_update: VendorUpdate) -> Vendor:
    """
    Update vendor details in the database.

    - **db**: The database session for performing database operations.
    - **vendor_id**: UUID of the vendor to update.
    - **vendor_update**: VendorUpdate schema containing the updated data.
    - Executes a query to find the vendor by its ID.
    - Updates only the fields provided in the VendorUpdate schema.
    - Commits the changes to the database and refreshes the vendor instance.
    - Raises a 404 HTTPException if the vendor is not found.
    - Returns the updated vendor.
    """
    vendor = await db.execute(select(Vendor).filter(Vendor.vendor_id == vendor_id))  # Query for the vendor by ID
    vendor = vendor.scalars().first()  # Retrieve the first result
    if not vendor:  # Check if the vendor exists
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Update the vendor's attributes with the provided data
    for key, value in vendor_update.dict(exclude_unset=True).items():
        setattr(vendor, key, value)

    await db.commit()  # Commit the changes to the database
    await db.refresh(vendor)  # Refresh the vendor instance
    return vendor


async def delete_vendor_from_db(db: AsyncSession, vendor_id: UUID) -> None:
    """
    Delete a vendor by its ID.

    - **db**: The database session for performing database operations.
    - **vendor_id**: UUID of the vendor to delete.
    - Executes a query to find the vendor by its ID.
    - Deletes the vendor from the database.
    - Commits the changes to the database.
    - Raises a 404 HTTPException if the vendor is not found.
    """
    vendor = await db.execute(select(Vendor).filter(Vendor.vendor_id == vendor_id))  # Query for the vendor by ID
    vendor = vendor.scalars().first()  # Retrieve the first result
    if not vendor:  # Check if the vendor exists
        raise HTTPException(status_code=404, detail="Vendor not found")

    await db.delete(vendor)  # Delete the vendor from the database
    await db.commit()  # Commit the changes
