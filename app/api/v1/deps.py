from typing import Literal
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User as UserModel
from app.api.v1.routes.auth import get_current_user
from app.services.authz_service import enforce_permission

Action = Literal["read", "create", "update", "delete"]


def require_permission(module_key: str, action: Action):
    """
    Factory de dependência para verificar permissões.
    
    Uso:
        @router.get("/users", dependencies=[Depends(require_permission("users", "read"))])
        def list_users(...):
            ...
    """
    def dependency(
        current_user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        enforce_permission(db, current_user, module_key, action)
        return current_user
    
    return dependency

