from typing import Annotated
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from src.api.core.dependencies import ListQueryParams
from src.api.core.utility import Print
from src.api.core.operation import listRecords, updateOp
from src.api.core.response import api_response, raiseExceptions
from src.api.models.categoryModel import (
    Category,
    CategoryCreate,
    CategoryRead,
    CategoryReadNested,
)
from src.api.core.dependencies import GetSession, requirePermission
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/category", tags=["Category"])


@router.post("/create")
def create(
    request: CategoryCreate, session: GetSession, user=requirePermission("category")
):
    data = Category(**request.model_dump())
    Print(data, "data")
    session.add(data)
    session.commit()
    session.refresh(data)
    return api_response(
        200, "Category Created Successfully", CategoryRead.model_validate(data)
    )


# @router.put("/update/{id}", response_model=RoleRead)
# def update_role(
#     id: int,
#     request: RoleUpdate,
#     session: GetSession,
#     user=requirePermission("role"),
# ):

#     role = session.get(Role, id)  # Like findById
#     raiseExceptions((role, 404, "Role not found"))
#     updateOp(role, request, session)

#     session.commit()
#     session.refresh(role)
#     return api_response(200, "Role Update Successfully", role)


# @router.get("/read/{id}")
# def get_user(
#     id: int,
#     session: GetSession,
#     user=requirePermission("role"),
# ):

#     role = session.get(Role, id)  # Like findById
#     raiseExceptions((role, 404, "Role not found"))

#     return api_response(200, "Role Found", role)


# ❗ DELETE
# @router.delete("/{id}", response_model=dict)
# def delete_user(
#     id: int,
#     session: GetSession,
#     user=requirePermission("role-delete"),
# ):
#     role = session.get(Role, id)
#     raiseExceptions((role, 404, "Role not found"))

#     session.delete(role)
#     session.commit()
#     return api_response(404, f"Role {role.title} deleted")


# ✅ LIST
@router.get("/list", response_model=list[CategoryReadNested])
def list(
    query_params: ListQueryParams,
    user=requirePermission("category"),
):
    query_params = vars(query_params)
    searchFields = [
        "title",
    ]
    result = listRecords(
        query_params=query_params,
        searchFields=searchFields,
        Model=Category,
        join_options=[selectinload(Category.children)],
    )
    categories = result["data"]
    if (
        categories and categories[0].parent_id
    ):  # assuming your search result is in `categories`
        # Treat the first search result as root by ignoring its parent
        categories[0].parent_id = None
    category_map = {
        c.id: CategoryReadNested(
            id=c.id,
            title=c.title,
            description=c.description,
            parent_id=c.parent_id,
            children=[],
        )
        for c in categories
    }
    roots = []

    # Step 1: attach children
    for cat in category_map.values():
        if cat.parent_id and cat.id != cat.parent_id:  # has a parent
            parent = category_map.get(cat.parent_id)
            if parent:
                if not any(child.id == cat.id for child in parent.children):
                    parent.children.append(cat)
        # ❌ DO NOT append to roots here

    # Step 2: collect only roots
    for cat in category_map.values():
        if not cat.parent_id:  # no parent_id means it's a root
            roots.append(cat)

    return api_response(200, "Users found", roots, result["total"])
