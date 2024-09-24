from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from . import crud, schemas, database

router = APIRouter()
@router.post("/orders/", response_model=schemas.OrderResponse)
def create_order(order: schemas.OrderCreate, db: Session = Depends(database.get_db)):
    return crud.create_order(db=db, order=order)

@router.get("/orders/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, db: Session = Depends(database.get_db)):
    return crud.get_order(db=db, order_id=order_id)