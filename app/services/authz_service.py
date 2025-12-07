from typing import Literal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.role import Role
from app.models.module import Module
from app.models.role_module_permission import RoleModulePermission

Action = Literal["read", "create", "update", "delete"]


def is_super_admin(user: User) -> bool:
    """Verifica se o usuário é Super Admin"""
    if not user.role:
        return False
    return user.role.key == "SUPER_ADMIN"


def has_permission(
    db: Session,
    user: User,
    module_key: str,
    action: Action
) -> bool:
    """
    Verifica se o usuário tem permissão para executar uma ação em um módulo.
    
    Args:
        db: Sessão do banco de dados
        user: Usuário atual
        module_key: Chave do módulo (ex: "users", "access_control")
        action: Ação a verificar ("read", "create", "update", "delete")
    
    Returns:
        True se tiver permissão, False caso contrário
    """
    # Super Admin tem acesso total
    if is_super_admin(user):
        return True
    
    # Se não tiver role, não tem permissão
    if not user.role:
        return False
    
    # Buscar permissão específica
    permission = db.query(RoleModulePermission).join(Module).filter(
        RoleModulePermission.role_id == user.role_id,
        Module.key == module_key
    ).first()
    
    if not permission:
        return False
    
    # Verificar ação específica
    action_map = {
        "read": permission.can_read,
        "create": permission.can_create,
        "update": permission.can_update,
        "delete": permission.can_delete,
    }
    
    return action_map.get(action, False)


def enforce_permission(
    db: Session,
    user: User,
    module_key: str,
    action: Action
) -> None:
    """
    Força a verificação de permissão, lançando HTTPException 403 se não tiver.
    
    Args:
        db: Sessão do banco de dados
        user: Usuário atual
        module_key: Chave do módulo
        action: Ação a verificar
    
    Raises:
        HTTPException: 403 se não tiver permissão
    """
    if not has_permission(db, user, module_key, action):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {action} on {module_key}"
        )

