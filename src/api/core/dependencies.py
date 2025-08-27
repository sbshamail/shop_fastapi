from typing import Annotated, Any, Dict

from fastapi import Depends
from sqlmodel import Session

from src.lib.db_con import get_session
# from src.mvc.core.security import require_permission, require_signin, require_admin


GetSession = Annotated[Session, Depends(get_session)]

# requireSignin = Depends(require_signin)
# requireAdmin = Annotated[dict, Depends(require_admin)]


# def requirePermission(permission: str):
#     return Depends(require_permission(permission))
