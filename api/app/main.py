import time 
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from .database import engine, Base, get_db
from .models import Products

app = FastAPI(title="FastAPI + MySQL", version="1.0.0")

@app.on_event("startup")
def starup_db_client():
    retries = 5
    while retries > 0:
        try:
            Base.metadata.create_all(bind=engine)
            break
        except OperationalError:
            retries -= 1
            time.sleep(3)

@app.get("/api/products")
def list_products(db:Session = Depends(get_db)):
    return db.query(Products).all()

@app.post("/api/products")
def create_product(name:str, price: str, db: Session = Depends(get_db)):
    product = Products(name=name, price=price)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product