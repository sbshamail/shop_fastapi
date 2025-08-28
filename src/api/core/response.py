from typing import Any, Optional, Union

from fastapi import HTTPException
from fastapi.encoders import (
    jsonable_encoder,
)
from fastapi.responses import (
    JSONResponse,
)


def api_response(
    code: int,
    detail: str,
    data: Optional[Union[dict, list]] = None,
    total: Optional[int] = None,
):

    content = {
        "success": (1 if code < 300 else 0),
        "detail": detail,
        "data": jsonable_encoder(data),
    }

    if total is not None:
        content["total"] = total

    # Raise error if code >= 400
    if code >= 400:
        raise HTTPException(
            status_code=code,
            detail=detail,
        )

    return JSONResponse(
        status_code=code,
        content=content,
    )
