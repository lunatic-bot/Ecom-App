from fastapi import FastAPI, Depends
from db.database import database
import crud

app = FastAPI()

# Connect to database before each request
@app.on_event("startup")
async def startup():
    await database.connect()

# Disconnect from database after each request
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/users/")
async def create_user(name: str, email: str):
    return await crud.create_user(name=name, email=email)

@app.get("/users/{user_id}")
async def read_user(user_id: int):
    return await crud.get_user(user_id=user_id)
