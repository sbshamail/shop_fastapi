from typing import Annotated, List, Optional

from pydantic import EmailStr, model_validator, StringConstraints
from sqlmodel import Field, Relationship, SQLModel
from src.api.models.baseModel import TimeStampedModel, TimeStampReadModel
from src.api.models.roleModel import RoleRead


class User(TimeStampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str = Field(max_length=50)
    email: EmailStr
    password: str
    phone: Annotated[
        Optional[str],
        StringConstraints(pattern=r"^\d{11}$"),
        Field(description="User's Phone Number"),
    ]
    is_active: bool = Field(default=True)
    role_id: Optional[int] = Field(default=None, foreign_key="user_role.id")
    role: Optional["Role"] = Relationship(back_populates="users")
    products: List["Product"] = Relationship(back_populates="user")
    ratings: List["Rating"] = Relationship(back_populates="user")


class RegisterUser(SQLModel):
    full_name: str
    email: EmailStr
    password: str
    confirm_password: str

    @model_validator(mode="before")
    def check_password_match(cls, values):
        if values.get("password") != values.get("confirm_password"):
            raise ValueError("Passwords do not match")
        return values


class UserReadBase(TimeStampReadModel):
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None


class UserRead(UserReadBase):
    role: Optional[RoleRead] = None


class LoginRequest(SQLModel):
    email: EmailStr
    password: str


class UserUpdate(SQLModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None


class UpdateUserByAdmin(UserUpdate):
    role_id: Optional[int] = None
