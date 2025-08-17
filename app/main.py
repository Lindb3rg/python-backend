from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import create_engine, SQLModel, Session, select
from app.db_tools import seed_products

from app.model import (
    Product,
    ProductCreate,
    ProductPublic,
    ProductUpdate,
    Order,
    OrderCreate,
    OrderPublic,
    OrderUpdate,
    OrderResponse,
    OrderDetail,
)

# OrdersCreate, OrdersResponse,

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
    with Session(engine) as session:
        seed_products(session)

    yield

    # Use this to drop DB everytime the app is closed
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


@app.get("/products/{product_id}", response_model=ProductPublic)
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


@app.patch("/products/{product_id}", response_model=ProductPublic)
def update_product(product_id: int, product: ProductUpdate, session: SessionDep):

    product_data = product.model_dump(exclude_unset=True)
    if not product_data:
        raise HTTPException(status_code=422, detail="Unprocessable Entity")

    product_db = session.get(Product, product_id)
    if not product_db:
        raise HTTPException(status_code=404, detail="Product not found")

    product_db.sqlmodel_update(product_data)
    session.add(product_db)
    session.commit()
    session.refresh(product_db)
    return product_db


@app.post("/orders/", response_model=OrderResponse)
def create_order(order_data: OrderCreate, session: SessionDep):

    print("order data: ", order_data)
    print("order data: ", type(order_data))

    total_amount = 0.0
    order_items_data = []

    for item in order_data.items:

        product = session.get(Product, item.product_id)
        if not product:
            raise HTTPException(
                status_code=404, detail=f"Product with ID {item.product_id} not found"
            )

        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.name}. Available: {product.stock_quantity}, Requested: {item.quantity}",
            )

        subtotal = product.unit_price * item.quantity
        total_amount += subtotal

        order_items_data.append(
            {
                "product": product,
                "quantity": item.quantity,
                "unit_price": product.unit_price,
                "subtotal": subtotal,
            }
        )

    try:

        new_order = Order(
            customer_name=order_data.customer_name,
            customer_email=order_data.customer_email,
            status="pending",
            authentication_string=order_data.authentication_string,
            total_amount=total_amount,
        )

        session.add(new_order)
        session.flush()

        for item_data in order_items_data:
            order_item = OrderDetail(
                order_id=new_order.id,
                product_id=item_data["product"].id,
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                subtotal=item_data["subtotal"],
            )
            session.add(order_item)

        for item_data in order_items_data:
            product = item_data["product"]
            product.stock_quantity -= item_data["quantity"]
            product.updated_at = datetime.utcnow()

        session.commit()
        session.refresh(new_order)

        return new_order

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")


# @app.post("/multple-orders/", response_model=OrdersResponse)
# def create_orders(orders_data: OrdersCreate, session: SessionDep):

#     breakpoint()
#     print(">>>>>>>>>> ORDERS DATA: ",orders_data)


#     for order in orders_data.order_list:


#         total_amount = 0.0
#         order_items_data = []

#         for item in order.items:

#             product = session.get(Product, item.product_id)
#             if not product:
#                 raise HTTPException(status_code=404, detail=f"Product with ID {item.product_id} not found")

#             if product.stock_quantity < item.quantity:
#                 raise HTTPException(
#                     status_code=400,
#                     detail=f"Insufficient stock for {product.name}. Available: {product.stock_quantity}, Requested: {item.quantity}"
#                 )

#             subtotal = product.unit_price * item.quantity
#             total_amount += subtotal

#             order_items_data.append({
#                 "product": product,
#                 "quantity": item.quantity,
#                 "unit_price": product.unit_price,
#                 "subtotal": subtotal
#             })

#         try:

#             new_order = Order(
#                 customer_name=order.customer_name,
#                 customer_email=order.customer_email,
#                 status="pending",
#                 authentication_string=order.authentication_string,
#                 total_amount=total_amount
#             )


#             session.add(new_order)
#             session.flush()


#             for item_data in order_items_data:
#                 order_item = OrderDetail(
#                     order_id=new_order.id,
#                     product_id=item_data["product"].id,
#                     quantity=item_data["quantity"],
#                     unit_price=item_data["unit_price"],
#                     subtotal=item_data["subtotal"]
#                 )
#                 session.add(order_item)


#             for item_data in order_items_data:
#                 product = item_data["product"]
#                 product.stock_quantity -= item_data["quantity"]
#                 product.updated_at = datetime.utcnow()

#             session.commit()
#             session.refresh(new_order)

#             return new_order

#         except Exception as e:
#             session.rollback()
#             raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")


@app.get("/orders/", response_model=list[OrderPublic])
def read_orders(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    orders = session.exec(select(Order).offset(offset).limit(limit)).all()
    return orders


@app.get("/orders/{order_id}", response_model=OrderPublic)
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

    order_details = session.exec(
        select(OrderDetail).where(OrderDetail.order_id == order_id)
    ).all()

    for detail in order_details:
        product = session.get(Product, detail.product_id)
        product.stock_quantity += detail.quantity
        session.add(product)
        session.delete(detail)

    session.delete(order)
    session.commit()
    return {"ok": True}


@app.patch("/orders/{order_id}", response_model=OrderPublic)
def update_order(order_id: int, order: OrderUpdate, session: SessionDep):

    order_data = order.model_dump(exclude_unset=True)
    if not order_data:
        raise HTTPException(status_code=422, detail="Unprocessable Entity")

    order_db = session.get(Order, order_id)
    if not order_db:
        raise HTTPException(status_code=404, detail="Order not found")

    order_db.sqlmodel_update(order_data)
    session.add(order_db)
    session.commit()
    session.refresh(order_db)
    return order_db
