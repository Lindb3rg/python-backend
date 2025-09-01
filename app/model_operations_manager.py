from enum import Enum

from .orders import (
    create_order_batch,
    delete_order,
    get_order,
    get_orders,
    update_order,
)
from .products import (
    create_product,
    delete_product,
    get_product,
    list_products,
    update_product,
)


class Operation(Enum):
    POST = "post"
    GET = "get"
    LIST = "list"
    DELETE = "delete"
    UPDATE = "update"


class ModelType(Enum):
    PRODUCT = "product"
    ORDER = "order"


from fastapi import HTTPException
from .logging_config import app_logger as logger


def operation_router(**current_model):

    if current_model["model_type"].value == "product":
        return product_manager(current_model)
    elif current_model["model_type"].value == "order":
        return order_manager(current_model)
    else:
        logger.warning(f"Model class type not found")
        raise HTTPException(status_code=404, detail="Model class not found ")


def product_manager(current_model):

    if current_model["operation"].value == "post":
        return create_product(current_model)

    elif current_model["operation"].value == "get":
        return get_product(current_model)

    elif current_model["operation"].value == "list":
        return list_products(current_model)

    elif current_model["operation"].value == "delete":
        return delete_product(current_model)

    elif current_model["operation"].value == "update":
        return update_product(current_model)

    else:
        logger.warning(f"Operation not found")
        raise ValueError(
            f"Invalid operation: {current_model['operation']},{current_model}. Supported operations are: {list(Operation)}"
        )


def order_manager(current_model):

    if current_model["operation"].value == "post":
        return create_order_batch(current_model)

    elif current_model["operation"].value == "list":
        return get_orders(current_model)

    elif current_model["operation"].value == "delete":
        return delete_order(current_model)

    elif current_model["operation"].value == "get":
        return get_order(current_model)

    elif current_model["operation"].value == "update":
        return update_order(current_model)
    else:
        logger.warning(f"Operation not found")
        raise ValueError(
            f"Invalid operation: {current_model['operation']},{current_model}. Supported operations are: {list(Operation)}"
        )
