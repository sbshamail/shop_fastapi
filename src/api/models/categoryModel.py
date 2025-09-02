from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel
from src.api.models.baseModel import TimeStampReadModel, TimeStampedModel


class Category(TimeStampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, unique=True, max_length=100)
    description: Optional[str] = None

    parent_id: Optional[int] = Field(default=None, foreign_key="category.id")
    parent: Optional["Category"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Category.id"},
    )
    children: List["Category"] = Relationship(back_populates="parent")
    products: List["Product"] = Relationship(back_populates="category")


class CategoryCreate(SQLModel):
    title: str
    description: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryRead(TimeStampReadModel):
    id: int
    title: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True  # enable ORM mode / attribute mapping


class CategoryReadNested(TimeStampReadModel):
    id: int
    title: str
    description: str | None = None
    parent_id: int | None = None
    children: list["CategoryReadNested"] = Field(default_factory=list)

    class Config:
        from_attributes = True
