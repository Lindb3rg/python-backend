from typing import Optional
from datetime import datetime, date

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select,Relationship

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, index=True)
    category: str = Field(max_length=255, index=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationship to order_details
    order_details: list["OrderDetail"] = Relationship(back_populates="product")


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_name: str = Field(max_length=100)
    customer_email: str = Field(max_length=100)
    order_date: Optional[date] = None
    status: str = Field(max_length=100)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationship to order_details
    order_details: list["OrderDetail"] = Relationship(back_populates="order")


class OrderDetail(SQLModel, table=True):
    __tablename__ = "order_details"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    order_id: int = Field(foreign_key="order.id")
    quantity: int  # smallint maps to int in Python
    unit_price: float  # real maps to float in Python
    subtotal: float  # real maps to float in Python
    
    # Relationships
    product: Optional[Product] = Relationship(back_populates="order_details")
    order: Optional[Order] = Relationship(back_populates="order_details")
    
    
