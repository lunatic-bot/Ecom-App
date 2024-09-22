from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from databases import Database
from config import settings

DATABASE_URL = settings.DATABASE_URL

database = Database(DATABASE_URL)
metadata = MetaData()

# SQLAlchemy models
Base = declarative_base()

engine = create_engine(
    settings.DATABASE_URL.replace("asyncpg", "psycopg2")
    )


