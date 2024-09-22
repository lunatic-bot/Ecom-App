from app.db.database import async_engine
from app.db.models.users import Base

# This creates all tables that are defined in your models
Base.metadata.create_all(bind=async_engine)