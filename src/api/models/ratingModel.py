from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint
from src.api.models.baseModel import TimeStampedModel


class Rating(TimeStampedModel, table=True):
    __table_args__ = (
        UniqueConstraint("product_id", "user_id", name="uq_product_user_rating"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)

    score: int = Field(ge=1, le=5)  # 1-5 stars
    comment: Optional[str] = None
    product_id: int = Field(foreign_key="product.id")
    user_id: int = Field(foreign_key="user.id")

    product: Optional["Product"] = Relationship(back_populates="ratings")
    user: Optional["User"] = Relationship(back_populates="ratings")


class RatingCreate(SQLModel):
    score: int = Field(ge=1, le=5)
    comment: Optional[str] = None


class RatingUpdate(SQLModel):
    score: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = None


class ProductRatingRead(SQLModel):
    product_id: int
    avg_rating: Optional[float] = 0


class ProductAllRating(SQLModel):
    id: int
    avg_rating: Optional[float] = 0
    ratings: Optional[List[Rating]] = None
