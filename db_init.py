from db.database import engine
from models.users import Base

# This creates all tables that are defined in your models
Base.metadata.create_all(bind=engine)