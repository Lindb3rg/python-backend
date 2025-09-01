from datetime import datetime
from fastapi import HTTPException
from sqlmodel import select
from app.model import Order, OrderBatch, OrderDetail, Product
from .logging_config import app_logger as logger


def create_order_batch(orders):

    orders_data = orders["orders_data"]
    session = orders["session"]

    order_batch = OrderBatch()

    logger.info(f"Creating order batch with {len(orders_data.order_list)} orders")

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


def get_orders(orders):

    session = orders["session"]
    offset = orders["offset"]
    limit = orders["limit"]

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


def get_order(order):

    session = order["session"]
    order_id = order["order_id"]

    order = session.get(Order, order_id)
    if not order:
        logger.warning(f"Order {order_id} not found")
        raise HTTPException(status_code=404, detail="Order not found")

    logger.info(f"Order {order_id} retrieved successfully")
    return order


def delete_order(order):

    session = order["session"]
    order_id = order["order_id"]

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


def update_order(order):

    order_to_update = order["update_order"]
    order_id = order["order_id"]
    session = order["session"]

    order_data = order_to_update.model_dump(exclude_unset=True)
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
