from fastapi import HTTPException
from sqlmodel import select
from app.model import Product
from .logging_config import app_logger as logger


def create_product(new_product):

    create_product = new_product["create_product"]
    session = new_product["session"]
    current_user = new_product["current_user"]

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
            extra={"product_id": product.id, "user_email": current_user.email},
        )
        return product

    except Exception as e:
        session.rollback()
        logger.error(f"Database error creating product: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create product")


def list_products(products):
    session = products["session"]
    offset = products["offset"]
    limit = products["limit"]
    products = session.exec(select(Product).offset(offset).limit(limit)).all()
    logger.info(
        f"Retrieved {len(products)} products",
        extra={"count": len(products), "offset": offset, "limit": limit},
    )
    return products


def get_product(current_product):
    session = current_product["session"]
    product_id = current_product["product_id"]

    product = session.get(Product, product_id)
    if not product:
        logger.warning(f"Product {product_id} not found")
        raise HTTPException(status_code=404, detail="Product not found")
    return product



def delete_product(product):
    session = product["session"]
    product_id = product["product_id"]
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


def update_product(product_for_update):

    product = product_for_update["update_product"]
    product_id = product_for_update["product_id"]
    session = product_for_update["session"]

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
