from typing import Optional
from fastapi import (
    APIRouter,
    Query,
    Request,
)
from sqlalchemy import select

from src.api.core import listRecords, updateOp, requireSignin
from src.api.core.dependencies import GetSession
from src.api.core.response import api_response
from src.api.models.userModel import User, UserRead, UserUpdate


router = APIRouter(prefix="/user", tags=["user"])


# ✅ READ ALL
@router.get("/list", response_model=list[UserRead])  # no response_model
def list_users(request: Request):
    query_params = dict(request.query_params)
    searchFields = [
        "full_name",
        "email",
        "phone",
        "role.title",
    ]
    return listRecords(
        query_params=query_params,
        searchFields=searchFields,
        Model=User,
        Schema=UserRead,
    )


@router.put("/update", response_model=UserRead)
def update_user(
    user: requireSignin,
    request: UserUpdate,
    session: GetSession,
):
    user_id = user.get("id")
    db_user = session.get(User, user_id)  # Like findById

    if not db_user:
        return api_response(404, "User not found")
    updateOp(db_user, request, session)

    session.commit()
    session.refresh(db_user)
    return api_response(200, "User Found", UserRead.model_validate(db_user))


@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: int,
    session: GetSession,
):
    user = session.get(User, user_id)  # Like findById
    if not user:
        # raise HTTPException(status_code=404, detail="User not found")
        return api_response(404, "User not found")
    return api_response(200, "User Found", user)
