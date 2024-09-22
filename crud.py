# crud.py
from sqlalchemy import select
from models.users import User
from db.database import database

async def get_user(user_id: int):
    query = select(User).where(User.id == user_id)
    return await database.fetch_one(query)

async def create_user(name: str, email: str):
    query = User.__table__.insert().values(name=name, email=email)
    return await database.execute(query)
