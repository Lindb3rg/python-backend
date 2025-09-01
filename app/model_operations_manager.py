from enum import Enum

from app.products import (
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
    elif current_model["create_product"].value == "order":
        pass
    else:
        logger.warning(f"Model class type not found")
        raise HTTPException(status_code=404, detail="Model class not found ")


def product_manager(current_model):

    if current_model["operation"].value == "post":
        logger.info(current_model["operation"])
        return create_product(current_model)

    elif current_model["operation"].value == "get":
        logger.info(current_model["operation"])
        return get_product(current_model)

    elif current_model["operation"].value == "list":
        logger.info(current_model["operation"])
        return list_products(current_model)

    elif current_model["operation"].value == "delete":
        logger.info(current_model["operation"])
        return delete_product(current_model)

    elif current_model["operation"].value == "update":
        logger.info(current_model["operation"])
        return update_product(current_model)

    else:
        logger.warning(f"Operation not found")
        raise ValueError(
            f"Invalid operation: {current_model['operation']},{current_model}. Supported operations are: {list(Operation)}"
        )


def order_manager(current_model):

    if current_model["operation"] == "post":
        pass
    elif current_model["operation"] == "get":
        pass
    elif current_model["operation"] == "delete":
        pass
    elif current_model["operation"] == "update":
        pass
    else:
        logger.warning(f"Operation not found")
        raise TypeError(status_code=404, detail="Operation not found")
