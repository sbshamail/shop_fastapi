from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy import select
from sqlmodel import Session

from src.api.models.userModel import User

ALGORITHM = "HS256"

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


## get user
def exist_user(db: Session, email: str):
    user = db.exec(select(User).where(User.email == email)).first()
    return user


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
