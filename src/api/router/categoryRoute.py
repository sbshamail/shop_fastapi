from fastapi import APIRouter, Request
from sqlalchemy import select
from src.api.core.pydantic import List_QueryParams
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
    request: Request,
    user=requirePermission("category"),
):
    query_params = dict(request.query_params)
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

    category_map = {
        c.id: CategoryReadNested.model_validate(c) for c in categories  # ✅ works now
    }
    print(category_map)
    roots = []

    for cat in category_map.values():
        if cat.parent_id:
            parent = category_map.get(cat.parent_id)
            if parent:
                # ✅ Prevent duplicates
                if not any(child.id == cat.id for child in parent.children):
                    parent.children.append(cat)
        else:
            if not any(root.id == cat.id for root in roots):
                roots.append(cat)

    return api_response(200, "Users found", roots, result["total"])
