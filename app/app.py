from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import create_engine, SQLModel, Session, select
from fastapi.middleware.cors import CORSMiddleware


from app.auth_client import User, get_current_user
from app.db_tools import seed_products

from .logging_config import setup_logging, app_logger as logger


from app.model import (
    OrderBatch,
    OrderBatchCreate,
    OrderBatchResponse,
    Product,
    ProductCreate,
    ProductPublic,
    ProductUpdate,
    Order,
    OrderPublic,
    OrderUpdate,
    OrderDetail,
)


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
def get_categories(session: SessionDep,current_user: User = Depends(get_current_user)):
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

    product = Product.model_validate(create_product, strict=True)

    existing_product = session.exec(
        select(Product).where(Product.name == product.name)
    ).first()

    if existing_product:
        logger.warning(f"Product '{product.name}' already exists")
        raise HTTPException(
            status_code=409, detail=f"Product '{product.name}' already exists"
        )

    try:
        session.add(product)
        session.commit()
        session.refresh(product)
        logger.success(
            f"Product '{product.name}' created by {current_user.email}", 
            extra={"product_id": product.id, "user_email": current_user.email}
        )
        return product

    except Exception as e:
        session.rollback()
        logger.error(f"Database error creating product: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create product")


@app.get("/products/", response_model=list[ProductPublic])
def read_products(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    current_user: User = Depends(get_current_user),
):
    products = session.exec(select(Product).offset(offset).limit(limit)).all()
    logger.info(
        f"Retrieved {len(products)} products",
        extra={"count": len(products), "offset": offset, "limit": limit},
    )
    return products


@app.get("/products/{product_id}", response_model=ProductPublic)
def read_product(
    product_id: int, session: SessionDep, current_user: User = Depends(get_current_user)
) -> Product:
    product = session.get(Product, product_id)
    if not product:
        logger.warning(f"Product {product_id} not found")
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.delete("/products/{product_id}")
def delete_product(
    product_id: int, session: SessionDep, current_user: User = Depends(get_current_user)
):
    product = session.get(Product, product_id)
    if not product:
        logger.warning(f"Product {product_id} not found for deletion")
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        product_name = product.name
        session.delete(product)
        session.commit()
        logger.success(
            f"Product '{product_name}' deleted successfully",
            extra={"product_id": product_id},
        )
        return {"ok": True}

    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete product: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete product: {str(e)}"
        )


@app.patch("/products/{product_id}", response_model=ProductPublic)
def update_product(
    product_id: int,
    product: ProductUpdate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):

    product_data = product.model_dump(exclude_unset=True)
    if not product_data:
        logger.warning(
            f"No data provided for product update", extra={"product_id": product_id}
        )
        raise HTTPException(status_code=422, detail="Unprocessable Entity")

    product_db = session.get(Product, product_id)
    if not product_db:
        logger.warning(f"Product {product_id} not found for update")
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        product_db.sqlmodel_update(product_data)
        session.commit()
        session.refresh(product_db)
        logger.success(
            f"Updated product successfully", extra={"product_id": product_db.id}
        )
        return product_db

    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update product: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update product: {str(e)}"
        )


@app.get("/orders/", response_model=list[OrderPublic])
def read_orders(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    current_user: User = Depends(get_current_user),
):
    try:
        orders = session.exec(select(Order).offset(offset).limit(limit)).all()
        logger.info(
            f"Retrieved {len(orders)} orders",
            extra={"count": len(orders), "offset": offset, "limit": limit},
        )
        return orders

    except Exception as e:
        logger.error(f"Database error retrieving orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve orders")


@app.get("/orders/{order_id}", response_model=OrderPublic)
def read_order(
    order_id: int, session: SessionDep, current_user: User = Depends(get_current_user)
) -> Order:
    order = session.get(Order, order_id)
    if not order:
        logger.warning(f"Order {order_id} not found")
        raise HTTPException(status_code=404, detail="Order not found")

    logger.info(f"Order {order_id} retrieved successfully")
    return order





@app.delete("/orders/{order_id}")
def delete_order(
    order_id: int, session: SessionDep, current_user: User = Depends(get_current_user)
):
    order = session.get(Order, order_id)
    if not order:
        logger.warning(f"Order {order_id} not found for deletion")
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        order_details = session.exec(
            select(OrderDetail).where(OrderDetail.order_id == order_id)
        ).all()

        for detail in order_details:
            product = session.get(Product, detail.product_id)
            if product:
                product.stock_quantity += detail.quantity

            session.delete(detail)

        session.delete(order)
        session.commit()

        logger.success(
            f"Order {order_id} and {len(order_details)} details deleted successfully"
        )
        return {"ok": True}

    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete order {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete order")


@app.patch("/orders/{order_id}", response_model=OrderPublic)
def update_order(
    order_id: int,
    order: OrderUpdate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):

    order_data = order.model_dump(exclude_unset=True)
    if not order_data:
        logger.warning(
            f"No data provided for order update", extra={"order_id": order_id}
        )
        raise HTTPException(status_code=422, detail="Unprocessable Entity")

    order_db = session.get(Order, order_id)
    if not order_db:
        logger.warning(f"Order {order_id} not found for update")
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        order_db.sqlmodel_update(order_data)
        session.commit()
        session.refresh(order_db)
        logger.success(
            f"Order {order_id} updated successfully", extra={"order_id": order_id}
        )
        return order_db

    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update order {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update order: {str(e)}")


@app.post("/orders/", response_model=OrderBatchResponse)
def create_order_batch(
    orders_data: OrderBatchCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):


    logger.info(f"Creating order batch with {len(orders_data.order_list)} orders")

    order_batch = OrderBatch()
    session.add(order_batch)
    session.flush()

    created_orders = []

    try:
        for order_idx, order in enumerate(orders_data.order_list):
            logger.info(
                f"Processing order {order_idx + 1}/{len(orders_data.order_list)} for {order.customer_email}"
            )

            total_amount = 0.0
            order_items_data = []

            for item in order.items:
                product = session.get(Product, item.product_id)
                if not product:
                    logger.error(
                        f"Product {item.product_id} not found in order {order_idx + 1}"
                    )
                    raise HTTPException(
                        status_code=404,
                        detail=f"Product with ID {item.product_id} not found",
                    )

                if product.stock_quantity < item.quantity:
                    logger.error(
                        f"Insufficient stock for {product.name}: {product.stock_quantity} < {item.quantity}"
                    )
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

            new_order = Order(
                customer_name=order.customer_name,
                customer_email=order.customer_email,
                status="pending",
                total_amount=total_amount,
                order_batch_id=order_batch.id,
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

            created_orders.append(new_order)
            logger.info(
                f"Order created for {order.customer_email} with total ${total_amount}"
            )

        session.commit()

        session.refresh(order_batch)
        for order in created_orders:
            session.refresh(order)

        logger.success(
            f"Order batch created successfully with {len(created_orders)} orders"
        )
        return order_batch

    except HTTPException:
        session.rollback()
        logger.error("Order batch creation failed due to business logic error")
        raise

    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error creating order batch: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create order batch")
