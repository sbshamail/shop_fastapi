from typing import Optional
from sqlmodel import Field, Relationship
from src.api.models.baseModel import TimeStampedModel


class Rating(TimeStampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    score: int = Field(ge=1, le=5)  # 1-5 stars
    comment: Optional[str] = None
    product_id: int = Field(foreign_key="product.id")
    user_id: int = Field(foreign_key="user.id")

    product: Optional["Product"] = Relationship(back_populates="ratings")
    user: Optional["User"] = Relationship(back_populates="ratings")
