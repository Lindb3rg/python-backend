
from datetime import datetime, date
from sqlmodel import Field, SQLModel, Relationship

class ProductBase(SQLModel):
    name: str = Field(max_length=255, index=True)
    category: str = Field(max_length=255, index=True)
    unit_price: float = 0
    stock_quantity: int = 0
    out_of_stock: bool = False


class Product(ProductBase, table=True):
    __tablename__ = "product"
    
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    authentication_string: str
    
    # Relationship to OrderDetail
    order_details: list["OrderDetail"] = Relationship(back_populates="product")

class ProductPublic(ProductBase):
    id: int

class ProductCreate(ProductBase):
    authentication_string: str


class ProductUpdate(ProductBase):
    name: str | None = None
    category: str | None = None
    unit_price: float | None = None
    stock_quantity: int | None = None
    updated_at: datetime | None = None
    authentication_string: str | None = None
    out_of_stock: bool | None = None







class OrderBase(SQLModel):
    customer_name: str = Field(max_length=100)
    customer_email: str = Field(max_length=100)
    status: str = Field(max_length=100, default="pending")
    


class Order(OrderBase, table=True):
    __tablename__ = "order"
    
    id: int | None = Field(default=None, primary_key=True)
    order_date: date = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    authentication_string: str
    total_amount: float
    order_details: list["OrderDetail"] = Relationship(back_populates="order")


class OrderPublic(OrderBase):
    id: int
    total_amount: float

class OrderCreate(OrderBase):
    items: list["OrderDetailRequest"]
    authentication_string: str


class OrderUpdate(OrderBase):
    customer_name: str | None = None
    customer_email: str | None = None
    status: str | None = None
    updated_at: datetime | None = None
    authentication_string: str | None = None
    total_amount: float | None = None

class OrderResponse(OrderBase):
    id: int
    customer_name: str
    customer_email: str
    status: str
    total_amount: float
    order_date: datetime
    authentication_string: str
    
    class Config:
        from_attributes = True



class OrderDetailBase(SQLModel):
    quantity: int
    unit_price: float
    subtotal: float

class OrderDetailRequest(SQLModel):
    product_id: int
    quantity: int
    
    

class OrderDetail(OrderDetailBase, table=True):
    __tablename__ = "order_details"
    
    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    order_id: int = Field(foreign_key="order.id")
    
    product: Product = Relationship(back_populates="order_details")
    order: Order = Relationship(back_populates="order_details")


class OrderDetailPublic(OrderDetailBase):
    id: int

class OrderDetailCreate(OrderDetailBase):
    product_id: int
    order_id: int


class OrderDetailUpdate(OrderDetailBase):
    quantity: int | None = None
    unit_price: float | None = None
    subtotal: float | None = None