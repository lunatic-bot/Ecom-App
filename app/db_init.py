# This creates all tables that are defined in your models
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from db.models.user import Base
from db.database import async_engine

# # Assuming async_engine is your asynchronous engine
# async def create_tables():
#     async with async_engine.begin() as conn:
#         # This will create all tables that are defined in your models
#         await conn.run_sync(Base.metadata.create_all)
        

# # To call this function
# import asyncio

# asyncio.run(create_tables())

# Assuming async_engine is your asynchronous engine
async def recreate_tables():
    async with async_engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

# To call this function
import asyncio

asyncio.run(recreate_tables())
