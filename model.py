from typing import Optional
from datetime import datetime, date
from sqlmodel import Field, SQLModel,Relationship

class ProductBase(SQLModel):
    name: str = Field(max_length=255, index=True)
    category: str = Field(max_length=255, index=True)
    unit_price: float
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationship to order_details
    # order_details: list["OrderDetail"] = Relationship(back_populates="product")


class Product(ProductBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    secret_name: str

class ProductPublic(ProductBase):
    id: int

class ProductCreate(ProductBase):
    secret_name: str


class ProductUpdate(ProductBase):
    name: str | None = None
    category: str | None = None
    unit_price: float | None = None
    updated_at: datetime | None = None
    secret_name: str | None = None


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
    quantity: int
    unit_price: float
    subtotal: float
    
    # Relationships
    product: Optional[Product] = Relationship(back_populates="order_details")
    order: Optional[Order] = Relationship(back_populates="order_details")
    
    
