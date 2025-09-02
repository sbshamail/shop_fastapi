from fastapi import APIRouter
from src.api.core.dependencies import GetSession, ListQueryParams, requireSignin
from src.api.core.operation import listRecords
from src.api.core.response import api_response
from src.api.models.productModel import Product, ProductCreate, ProductRead

router = APIRouter(prefix="/product", tags=["Product"])


@router.post("/create")
def create(request: ProductCreate, session: GetSession, user: requireSignin):
    data = Product(**request.model_dump())
    session.add(data)
    session.commit()
    session.refresh(data)
    return api_response(
        200, "Product Created Successfully", ProductRead.model_validate(data)
    )


@router.get("/list", response_model=list[ProductRead])
def list(
    query_params: ListQueryParams,
):
    query_params = vars(query_params)
    searchFields = [
        "title",
    ]
    return listRecords(
        query_params=query_params,
        searchFields=searchFields,
        Model=Product,
        Schema=ProductRead,
    )
