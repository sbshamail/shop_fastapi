from functools import wraps
import re
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError
from pydantic import ValidationError

from src.api.core.response import api_response


def handle_async_wrapper(func):
    """
    Wraps route handlers to catch and normalize exceptions.
    Keeps important ones explicit, logs the rest.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except ValidationError as ve:
            # Pydantic validation issues
            return api_response(
                422,
                content={"message": "Validation error", "details": ve.errors()},
            )
        except IntegrityError as ie:
            # Try to extract the short useful DB message
            msg = str(ie.orig) if ie.orig else str(ie)
            # If it's a unique violation, make it clean
            if "duplicate key value violates unique constraint" in msg:
                # optionally extract which field
                m = re.search(r"Key \((.*?)\)=\((.*?)\)", msg)
                if m:
                    field, value = m.groups()
                    msg = f"Duplicate entry: {field} = {value}"
                else:
                    msg = "Duplicate key violation"
            return api_response(409, msg)
        except OperationalError:
            # DB connectivity or operational issues
            return api_response(503, "Database unavailable, try again later")
        except Exception as e:
            # Catch-all for unexpected errors, logs for debugging
            # (you could also use logging here instead of printing)
            print(f"[ERROR] {e}")
            return api_response(500, "Internal Server Error")

    return wrapper
