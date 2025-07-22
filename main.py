from contextlib import asynccontextmanager
from typing import Union,Annotated
from fastapi import FastAPI,Depends, HTTPException,Query
from sqlmodel import create_engine,SQLModel,Session,select
import os

from model import Product

from dotenv import load_dotenv

load_dotenv()

sqlite_file_name = os.getenv("sqlite_file_name")




sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()

app = FastAPI(lifespan=lifespan)



@app.post("/products/")
def create_product(product: Product, session: SessionDep) -> Product:
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@app.get("/products/")
def read_products(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Product]:
    products = session.exec(select(Product).offset(offset).limit(limit)).all()
    return products


@app.get("/products/{product_id}")
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




