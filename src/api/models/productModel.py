from typing import List, Optional

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
    # images: List[str] = Field(default_factory=list)
    price: float
    sale_price: Optional[float] = None
    stock: int = Field(default=0)
    is_active: bool = Field(default=True)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="products")
    category: Optional["Category"] = Relationship(back_populates="products")
    ratings: List["Rating"] = Relationship(back_populates="product")


class ProductCreate(SQLModel):
    user_id: int
    category_id: int
    title: str = Field(max_length=100)
    description: Optional[str] = None
    price: float
    sale_price: Optional[float] = None
    stock: int = Field(default=0)
    is_active: bool = Field(default=True)


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
    ratings: Optional[List[Rating]] = None
    avg_rating: Optional[float] = None

    class Config:
        from_attributes = True
