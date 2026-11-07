import time
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from .database import engine, Base, get_db
from .models import Products

app = FastAPI(title="FastAPI + MySQL", version="1.1.0")


class ProductIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: str = Field(..., min_length=1, max_length=50)


@app.on_event("startup")
def startup_db_client():
    retries = 5
    while retries > 0:
        try:
            Base.metadata.create_all(bind=engine)
            break
        except OperationalError:
            retries -= 1
            time.sleep(3)


@app.get("/api/products")
def list_products(db: Session = Depends(get_db)):
    return db.query(Products).order_by(Products.id.desc()).all()


@app.get("/api/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Products, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@app.post("/api/products", status_code=201)
def create_product(data: ProductIn, db: Session = Depends(get_db)):
    product = Products(name=data.name.strip(), price=data.price.strip())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@app.put("/api/products/{product_id}")
def update_product(product_id: int, data: ProductIn, db: Session = Depends(get_db)):
    product = db.get(Products, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    product.name = data.name.strip()
    product.price = data.price.strip()
    db.commit()
    db.refresh(product)
    return product


@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Products, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(product)
    db.commit()
    return {"ok": True, "deleted_id": product_id}
