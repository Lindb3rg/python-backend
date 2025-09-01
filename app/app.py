from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import create_engine, SQLModel, Session, select
from fastapi.middleware.cors import CORSMiddleware


from app.model_operations_manager import operation_router
from app.auth_client import User, get_current_user
from app.db_tools import seed_products


from .logging_config import app_logger as logger
from .model_operations_manager import ModelType, Operation

from app.model import (
    OrderBatchCreate,
    OrderBatchResponse,
    Product,
    ProductCreate,
    ProductPublic,
    ProductUpdate,
    Order,
    OrderPublic,
    OrderUpdate,
)

model_operation = Operation
model_type = ModelType


sqlite_file_name = "database.db"
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
    logger.info("Application starting up")
    with Session(engine) as session:
        logger.info("Application shutting down")
        seed_products(session)

    yield

    # Use this to drop DB everytime the app is closed
    drop_db_and_tables()


app = FastAPI(lifespan=lifespan, debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/users/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/categories/", response_model=list[str])
def get_categories(session: SessionDep, current_user: User = Depends(get_current_user)):
    categories = session.exec(
        select(Product.category).where(Product.category.is_not(None)).distinct()
    ).all()
    return [cat for cat in categories if cat]


@app.post("/products/", response_model=ProductPublic)
def create_product(
    create_product: ProductCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    new_product = {
        "create_product": create_product,
        "session": session,
        "current_user": current_user,
        "operation": model_operation.POST,
        "model_type": model_type.PRODUCT,
    }

    try:
        product = operation_router(**new_product)
        return product
    except Exception as e:
        logger.error(f"Failed to create product: {str(e)}")


@app.get("/products/", response_model=list[ProductPublic])
def read_products(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    current_user: User = Depends(get_current_user),
):

    products = {
        "session": session,
        "offset": offset,
        "limit": limit,
        "operation": model_operation.LIST,
        "model_type": model_type.PRODUCT,
    }

    return operation_router(**products)


@app.get("/products/{product_id}", response_model=ProductPublic)
def read_product(
    product_id: int, session: SessionDep, current_user: User = Depends(get_current_user)
) -> Product:

    product = {
        "session": session,
        "operation": model_operation.GET,
        "model_type": model_type.PRODUCT,
        "product_id": product_id,
    }

    product = operation_router(**product)


@app.delete("/products/{product_id}")
def delete_product(
    product_id: int, session: SessionDep, current_user: User = Depends(get_current_user)
):

    product = {
        "session": session,
        "operation": model_operation.DELETE,
        "model_type": model_type.PRODUCT,
        "product_id": product_id,
    }

    return operation_router(**product)


@app.patch("/products/{product_id}", response_model=ProductPublic)
def update_product(
    product_id: int,
    product: ProductUpdate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):

    product = {
        "update_product": product,
        "session": session,
        "operation": model_operation.UPDATE,
        "model_type": model_type.PRODUCT,
        "product_id": product_id,
    }

    return operation_router(**product)


@app.get("/orders/", response_model=list[OrderPublic])
def read_orders(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    current_user: User = Depends(get_current_user),
):

    orders = {
        "session": session,
        "offset": offset,
        "limit": limit,
        "operation": model_operation.LIST,
        "model_type": model_type.ORDER,
    }

    return operation_router(**orders)


@app.get("/orders/{order_id}", response_model=OrderPublic)
def read_order(
    order_id: int, session: SessionDep, current_user: User = Depends(get_current_user)
) -> Order:

    order = {
        "session": session,
        "operation": model_operation.GET,
        "model_type": model_type.ORDER,
        "order_id": order_id,
    }

    return operation_router(**order)


@app.delete("/orders/{order_id}")
def delete_order(
    order_id: int, session: SessionDep, current_user: User = Depends(get_current_user)
):

    order = {
        "session": session,
        "operation": model_operation.DELETE,
        "model_type": model_type.ORDER,
        "order_id": order_id,
    }

    return operation_router(**order)


@app.patch("/orders/{order_id}", response_model=OrderPublic)
def update_order(
    order_id: int,
    order: OrderUpdate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):

    order = {
        "order_id": order_id,
        "update_order": order,
        "operation": model_operation.UPDATE,
        "session": session,
        "model_type": model_type.ORDER,
    }

    return operation_router(**order)


@app.post("/orders/", response_model=OrderBatchResponse)
def create_order_batch(
    orders_data: OrderBatchCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):

    order = {
        "orders_data": orders_data,
        "operation": model_operation.POST,
        "session": session,
        "model_type": model_type.ORDER,
    }

    return operation_router(**order)
