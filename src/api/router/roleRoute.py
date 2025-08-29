from fastapi import APIRouter, Request
from src.api.core.operation import listRecords, updateOp
from src.api.core.response import api_response, raiseExceptions
from src.api.models.roleModel import Role, RoleCreate, RoleRead, RoleUpdate
from src.api.core.dependencies import GetSession, requirePermission


router = APIRouter(prefix="/role", tags=["Role"])


@router.post("/create")
def create_role(
    request: RoleCreate, session: GetSession, user=requirePermission("role")
):
    role = Role(**request.model_dump())
    session.add(role)
    session.commit()
    session.refresh(role)
    return api_response(200, "Role Created Successfully", role)


@router.put("/update/{id}", response_model=RoleRead)
def update_role(
    id: int,
    request: RoleUpdate,
    session: GetSession,
    user=requirePermission("role"),
):

    role = session.get(Role, id)  # Like findById
    raiseExceptions((role, 404, "Role not found"))
    updateOp(role, request, session)

    session.commit()
    session.refresh(role)
    return api_response(200, "Role Update Successfully", role)


@router.get("/read/{id}")
def get_user(
    id: int,
    session: GetSession,
    user=requirePermission("role"),
):

    role = session.get(Role, id)  # Like findById
    raiseExceptions((role, 404, "Role not found"))

    return api_response(200, "Role Found", role)


# ❗ DELETE
@router.delete("/{id}", response_model=dict)
def delete_user(
    id: int,
    session: GetSession,
    user=requirePermission("role-delete"),
):
    role = session.get(Role, id)
    raiseExceptions((role, 404, "Role not found"))

    session.delete(role)
    session.commit()
    return api_response(404, f"Role {role.title} deleted")


# ✅ LIST
@router.get("/list", response_model=list[RoleRead])
def list(
    request: Request,
    user=requirePermission("role"),
):
    query_params = dict(request.query_params)
    searchFields = [
        "title",
    ]
    return listRecords(
        query_params=query_params,
        searchFields=searchFields,
        Model=Role,
        Schema=RoleRead,
    )
