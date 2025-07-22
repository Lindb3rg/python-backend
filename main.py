from contextlib import asynccontextmanager
from typing import Union,Annotated
from fastapi import FastAPI,Depends, HTTPException,Query
from sqlmodel import create_engine,SQLModel,Session,select
import os

from model import (Product,
                   ProductCreate,
                   ProductPublic,
                   ProductUpdate,
                   Order,
                   OrderCreate,
                   OrderPublic,
                   OrderUpdate,
                   OrderResponse)

from dotenv import load_dotenv

load_dotenv()



sqlite_file_name = os.getenv("sqlite_file_name")
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def drop_db_and_tables():
    SQLModel.metadata.drop_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]




@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    drop_db_and_tables()

app = FastAPI(lifespan=lifespan)


@app.post("/products/", response_model=ProductPublic)
def create_product(create_product: ProductCreate, session: SessionDep):
    db_product = Product.model_validate(create_product)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@app.get("/products/", response_model=list[ProductPublic])
def read_products(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    products = session.exec(select(Product).offset(offset).limit(limit)).all()
    return products


@app.get("/products/{product_id}",response_model=ProductPublic)
def read_product(product_id: int, session: SessionDep) -> Product:
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.delete("/products/{product_id}")
def delete_product(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(product)
    session.commit()
    return {"ok": True}


@app.patch("/products/{product_id}",response_model=ProductPublic)
def update_product(product_id: int, product: ProductUpdate, session: SessionDep):
    product_db = session.get(Product, product_id)
    if not product_db:
        raise HTTPException(status_code=404, detail="Product not found")
    product_data = product.model_dump(exclude_unset=True)
    product_db.sqlmodel_update(product_data)
    session.add(product_db)
    session.commit()
    session.refresh(product_db)
    return product_db






@app.post("/orders/", response_model=OrderResponse)
def create_order(create_order: OrderCreate, session: SessionDep):
    
    db_order = Order.model_validate(create_order)
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    return db_order


@app.get("/orders/", response_model=list[OrderPublic])
def read_orders(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    orders = session.exec(select(Order).offset(offset).limit(limit)).all()
    return orders


@app.get("/orders/{order_id}",response_model=OrderPublic)
def read_order(order_id: int, session: SessionDep) -> Order:
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.delete("/orders/{order_id}")
def delete_order(order_id: int, session: SessionDep):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    session.delete(order)
    session.commit()
    return {"ok": True}


@app.patch("/orders/{order_id}",response_model=OrderPublic)
def update_order(order_id: int, order: OrderUpdate, session: SessionDep):
    order_db = session.get(Order, order_id)
    if not order_db:
        raise HTTPException(status_code=404, detail="Order not found")
    order_data = order.model_dump(exclude_unset=True)
    order_db.sqlmodel_update(order_data)
    session.add(order_db)
    session.commit()
    session.refresh(order_db)
    return order_db





