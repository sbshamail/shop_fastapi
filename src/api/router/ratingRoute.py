from statistics import mean
from fastapi import APIRouter

from src.api.core.operation import listop, updateOp
from src.api.core.decorator import handle_async_wrapper
from src.api.core.dependencies import GetSession, ListQueryParams, requireSignin
from src.api.core.response import api_response, raiseExceptions

from src.api.models.productModel import Product
from src.api.models.ratingModel import (
    ProductAllRating,
    ProductRatingRead,
    Rating,
    RatingCreate,
    RatingUpdate,
)


router = APIRouter(prefix="/product/rating", tags=["Rating"])


@router.post("/create/{product_id}")
@handle_async_wrapper
def create(
    product_id: int, request: RatingCreate, session: GetSession, user: requireSignin
):

    data = Rating(**request.model_dump())
    data.product_id = product_id
    data.user_id = user.get("id")
    session.add(data)
    session.commit()
    session.refresh(data)
    product = session.get(Product, product_id)
    raiseExceptions((product, 404, "Product not found"))
    avg = 0.0
    if product.ratings:
        avg = float(mean([r.score for r in product.ratings]))

    return api_response(
        200,
        "Rating added Successfully",
        ProductRatingRead(product_id=product.id, avg_rating=avg),
    )


@router.put("/update/{id}", response_model=ProductRatingRead)
@handle_async_wrapper
def update(id: int, request: RatingUpdate, session: GetSession, user: requireSignin):

    rating = session.get(Rating, id)  # Like findById
    raiseExceptions((rating, 404, "Rating not found"))
    if rating.user_id != user.get("id") and user.get("role") != "admin":
        api_response(400, "You are not authorized to update this rating")

    updateOp(rating, request, session)

    session.commit()
    session.refresh(rating)
    product = session.get(Product, rating.product_id)
    raiseExceptions((product, 404, "Product not found"))
    avg = 0.0
    if product.ratings:
        avg = (
            float(mean([r.score for r in product.ratings])) if product.ratings else 0.0
        )
    return api_response(
        200,
        "Rating Update Successfully",
        ProductRatingRead(product_id=product.id, avg_rating=avg),
    )


@router.delete("/delete/{id}", response_model=ProductRatingRead)
@handle_async_wrapper
def delete(id: int, session: GetSession, user: requireSignin):

    rating = session.get(Rating, id)  # Like findById
    raiseExceptions((rating, 404, "Rating not found"))
    if rating.user_id != user.get("id") and user.get("role") != "admin":
        api_response(400, "You are not authorized to update this rating")

    session.delete(rating)
    session.commit()

    return api_response(200, "Rating Delete Successfully")


@router.get("/read/{product_id}")
@handle_async_wrapper
def get_role(
    product_id: int,
    session: GetSession,
    query_params: ListQueryParams,
    user=requireSignin,
):
    searchFields = ["comment"]

    product = session.get(Product, product_id)  # Like findById
    raiseExceptions((product, 404, "Product not found"))

    query_params = vars(query_params)
    dateRange = query_params.get("dateRange")
    searchTerm = query_params.get("searchTerm")
    columnFilters = query_params.get("columnFilters")
    numberRange = query_params.get("numberRange")
    page = int(query_params.get("page", 1))
    skip = int(query_params.get("skip", 0))
    limit = int(query_params.get("limit", 10))
    filters = {
        "searchTerm": searchTerm,
        "columnFilters": columnFilters,
        "dateRange": dateRange,
        "numberRange": numberRange,
        "customFilters": [["id", product_id]],
    }

    result = listop(
        session=session,
        Model=Product,
        searchFields=searchFields,
        filters=filters,
        skip=skip,
        page=page,
        limit=limit,
    )

    list_data = [ProductAllRating.model_validate(prod) for prod in result["data"]]
    product = list_data[0]
    avg = 0.0
    if product.ratings:
        avg = float(mean([r.score for r in product.ratings]))
    product.avg_rating = avg
    return api_response(
        200,
        "data found",
        product,
        result["total"],
    )
