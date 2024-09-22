from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from databases import Database
from config import settings
from fastapi import Depends

DATABASE_URL = settings.DATABASE_URL

# For async database connection
database = Database(DATABASE_URL)
metadata = MetaData()

# SQLAlchemy models
Base = declarative_base()

# Create an async SQLAlchemy engine
async_engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency to get the async database session
async def get_db() -> AsyncSession: # type: ignore 
    async with AsyncSessionLocal() as session:
        yield session



# from sqlalchemy import create_engine, MetaData
# from sqlalchemy.ext.declarative import declarative_base
# from databases import Database
# from config import settings

# DATABASE_URL = settings.DATABASE_URL

# database = Database(DATABASE_URL)
# metadata = MetaData()

# # SQLAlchemy models
# Base = declarative_base()

# engine = create_engine(
#     settings.DATABASE_URL.replace("asyncpg", "psycopg2")
#     )


