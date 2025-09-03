from fastapi import APIRouter
from src.api.core.dependencies import (
    GetSession,
    ListQueryParams,
    requireSignin,
    requirePermission,
)
from src.api.core.operation import listRecords, updateOp
from src.api.core.response import api_response, raiseExceptions
from src.api.models.productModel import (
    Product,
    ProductCreate,
    ProductRead,
    ProductUpdate,
)
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/product", tags=["Product"])


@router.post("/create")
def create(request: ProductCreate, session: GetSession, user: requireSignin):
    data = Product(**request.model_dump())
    data.user_id = user.get("id")
    session.add(data)
    session.commit()
    session.refresh(data)
    return api_response(
        200, "Product Created Successfully", ProductRead.model_validate(data)
    )


@router.get("/read/{id}", response_model=ProductRead)
def findOne(id: int, session: GetSession, auth=requirePermission("product")):

    read = session.get(Product, id)  # Like findById
    raiseExceptions((read, 404, "Product not found"))

    return api_response(200, "Product Found", ProductRead.model_validate(read))


@router.put("/update/{id}", response_model=dict)
def updateOne(
    id: int, request: ProductUpdate, session: GetSession, user: requireSignin
):
    product = session.get(Product, id)
    raiseExceptions((product, 404, "Product not found"))
    print(user.get("id") != product.user_id)
    role = user.get("role")

    if role == "admin" or user.get("id") == product.user_id:
        updateProduct = updateOp(product, request, session)
        return api_response(
            200,
            "Product update Successfully",
            ProductRead.model_validate(updateProduct),
        )
    else:
        raiseExceptions(
            (
                user.get("id") != product.user_id,
                400,
                "You are not authorized to update this product",
                True,
            )
        )


@router.delete("/delete/{id}", response_model=dict)
def deleteOne(id: int, session: GetSession, user: requireSignin):
    product = session.get(Product, id)
    raiseExceptions((product, 404, "Product not found"))
    print(user.get("id") != product.user_id)
    role = user.get("role")
    if role == "admin" or user.get("id") == product.user_id:
        session.delete(product)
        session.commit()
        return api_response(200, f'Product "{product.title}" deleted successfully')
    else:
        raiseExceptions(
            (
                user.get("id") != product.user_id,
                400,
                "You are not authorized to delete this product",
                True,
            )
        )


from fastapi import Body


@router.delete("/delete-many", response_model=dict)
def delete_many(
    session: GetSession,
    user: requireSignin,
    product_ids: list[int] = Body(
        ..., embed=True, description="List of product IDs to delete"
    ),
):
    deleted = []
    failed = []

    role = user.get("role")
    user_id = user.get("id")

    for pid in product_ids:
        instance = session.get(Product, pid)
        if not instance:
            failed.append({"id": pid, "reason": "not found"})
            continue

        # Permission check
        if role == "admin" or user_id == instance.user_id:
            session.delete(instance)
            deleted.append({"id": pid, "title": instance.title})
        else:
            failed.append(
                {"id": pid, "title": instance.title, "reason": "Unauthorized"}
            )

    # Commit all successful deletes at once
    session.commit()

    return api_response(
        200,
        "Bulk delete processed",
        {
            "deleted": deleted,
            "failed": failed,
            "summary": {
                "requested": len(product_ids),
                "deleted_count": len(deleted),
                "failed_count": len(failed),
            },
        },
    )


@router.get("/list", response_model=list[ProductRead])
def list(
    query_params: ListQueryParams,
):
    query_params = vars(query_params)
    searchFields = ["title", "description", "category.title"]
    return listRecords(
        query_params=query_params,
        searchFields=searchFields,
        Model=Product,
        Schema=ProductRead,
    )
