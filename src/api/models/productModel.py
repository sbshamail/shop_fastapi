from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel
from src.api.models.baseModel import TimeStampReadModel, TimeStampedModel
from src.api.models.userModel import UserReadBase
from src.api.models.categoryModel import Category, CategoryRead
from src.api.models.ratingModel import Rating


class Product(TimeStampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")

    title: str = Field(max_length=100)
    description: Optional[str] = None
    images: Optional[List[Dict[str, Any]]] = Field(sa_column=Column(JSON))
    price: float
    sale_price: Optional[float] = None
    stock: int = Field(default=0)
    is_active: bool = Field(default=True)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="products")
    category: Optional["Category"] = Relationship(back_populates="products")
    ratings: List["Rating"] = Relationship(back_populates="product")


class ProductCreate(SQLModel):
    category_id: int
    title: str = Field(max_length=100)
    description: Optional[str] = None
    price: float
    sale_price: Optional[float] = None
    stock: int = Field(default=0)
    is_active: bool = Field(default=True)
    images: Optional[List[Dict[str, Any]]]


class ProductUpdate(SQLModel):
    category_id: Optional[int] = None
    title: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = None
    sale_price: Optional[float] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None


class ProductRead(TimeStampReadModel):
    id: int
    user_id: int
    category_id: int
    title: str
    description: Optional[str]
    price: float
    sale_price: Optional[float]
    stock: int
    is_active: bool
    user: Optional[UserReadBase] = None
    category: Optional[CategoryRead] = None
    # ratings: Optional[List[Rating]] = None
    avg_rating: Optional[float] = None

    class Config:
        from_attributes = True
