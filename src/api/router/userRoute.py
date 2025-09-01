from typing import Optional
from fastapi import (
    APIRouter,
    Depends,
    Query,
    Request,
)
from sqlalchemy import select

from src.api.core.dependencies import ListQueryParams
from src.api.core.security import hash_password
from src.api.core import listRecords, updateOp, requireSignin
from src.api.core.dependencies import GetSession, requirePermission, requireAdmin
from src.api.core.response import api_response, raiseExceptions
from src.api.models.userModel import UpdateUserByAdmin, User, UserRead, UserUpdate


router = APIRouter(prefix="/user", tags=["user"])


@router.put("/update", response_model=UserRead)
def update_user(
    user: requireSignin,
    request: UserUpdate,
    session: GetSession,
):
    user_id = user.get("id")
    db_user = session.get(User, user_id)  # Like findById
    raiseExceptions((db_user, 404, "User not found"))
    update_user = updateOp(db_user, request, session)
    if request.password:
        hashed_password = hash_password(request.password)
        update_user.password = hashed_password
    session.commit()
    session.refresh(db_user)
    return api_response(200, "User Found", UserRead.model_validate(db_user))


@router.put("/updatebyadmin/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    request: UpdateUserByAdmin,
    session: GetSession,
    user=requirePermission("all"),
):
    db_user = session.get(User, user_id)  # Like findById
    raiseExceptions((db_user, 404, "User not found"))
    update_user = updateOp(db_user, request, session)
    if request.password:
        hashed_password = hash_password(request.password)
        update_user.password = hashed_password
    session.commit()
    session.refresh(update_user)
    return api_response(200, "User Found", UserRead.model_validate(update_user))


# ✅ READ ALL
@router.get("/list", response_model=list[UserRead])  # no response_model
def list_users(
    user: requireAdmin,
    query_params: ListQueryParams,
):
    # query_params = dict(request.query_params)

    query_params = vars(query_params)
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


@router.get("/read", response_model=User)
def get_user(
    user: requireSignin,
    session: GetSession,
):
    user_id = user.get("id")
    db_user = session.get(User, user_id)  # Like findById
    raiseExceptions((db_user, 400, "User not found"))
    return api_response(200, "User Found", db_user)


# ✅ DELETE
@router.delete("/{user_id}", response_model=dict)
def delete_user(
    user_id: int,
    session: GetSession,
    user=requirePermission("all"),
):
    db_user = session.get(User, user_id)
    raiseExceptions((db_user, 400, "User not found"))

    session.delete(db_user)
    session.commit()
    return api_response(404, f"User {user_id} deleted")
