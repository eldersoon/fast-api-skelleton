from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User as UserModel
from app.api.v1.routes.auth import get_current_user
from app.api.v1.deps import require_permission
from app.schemas.role import Role, RoleCreate, RoleUpdate
from app.schemas.module import Module
from app.schemas.user import User
from app.schemas.permission import (
    RolePermissionMatrix,
    PermissionBulkUpdate,
    UserRoleUpdate
)
from app.schemas.response import GetResponse, ListResponse
from app.core.responses import get_response, list_response, error_response, error_detail
from app.services.role_service import (
    get_role,
    get_roles,
    create_role,
    update_role
)
from app.services.module_service import get_modules
from app.services.permission_service import (
    get_role_permission_matrix,
    update_role_permissions
)
from app.services.user_service import get_user, update_user as update_user_service
from app.services.authz_service import is_super_admin

router = APIRouter()


@router.get("/modules", response_model=ListResponse[Module])
def list_modules(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_permission("access_control", "read"))
):
    """Lista todos os módulos do sistema"""
    modules = get_modules(db)
    return list_response(
        items=modules,
        total=len(modules),
        page=1,
        per_page=len(modules),
        message="Modules retrieved successfully"
    )


@router.get("/roles", response_model=ListResponse[Role])
def list_roles(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_permission("access_control", "read"))
):
    """Lista todos os roles"""
    roles = get_roles(db)
    return list_response(
        items=roles,
        total=len(roles),
        page=1,
        per_page=len(roles),
        message="Roles retrieved successfully"
    )


@router.get("/roles/{role_id}/permissions", response_model=GetResponse[RolePermissionMatrix])
def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_permission("access_control", "read"))
):
    """Obtém a matriz de permissões de um role"""
    matrix = get_role_permission_matrix(db, role_id)
    if not matrix:
        return error_response(
            message="Role not found",
            status_code=status.HTTP_404_NOT_FOUND,
            errors=[error_detail(message=f"Role with ID {role_id} not found")]
        )
    
    return get_response(
        data=matrix,
        message="Role permissions retrieved successfully"
    )


@router.put("/roles/{role_id}/permissions", response_model=GetResponse[RolePermissionMatrix])
def update_role_permissions_route(
    role_id: int,
    permissions: PermissionBulkUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_permission("access_control", "update"))
):
    """Atualiza as permissões de um role"""
    # Verificar se role existe
    role = get_role(db, role_id)
    if not role:
        return error_response(
            message="Role not found",
            status_code=status.HTTP_404_NOT_FOUND,
            errors=[error_detail(message=f"Role with ID {role_id} not found")]
        )
    
    # Não permite atualizar permissões de SUPER_ADMIN (exceto se for super admin)
    if role.key == "SUPER_ADMIN" and not is_super_admin(current_user):
        return error_response(
            message="Permission denied",
            status_code=status.HTTP_403_FORBIDDEN,
            errors=[error_detail(message="Cannot modify SUPER_ADMIN permissions")]
        )
    
    success = update_role_permissions(db, role_id, permissions.permissions)
    if not success:
        return error_response(
            message="Failed to update permissions",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Retornar matriz atualizada
    matrix = get_role_permission_matrix(db, role_id)
    return get_response(
        data=matrix,
        message="Role permissions updated successfully"
    )


@router.patch("/users/{user_id}/role", response_model=GetResponse[User])
def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_permission("access_control", "update"))
):
    """Atualiza o role de um usuário"""
    # Verificar se usuário existe
    user = get_user(db, user_id)
    if not user:
        return error_response(
            message="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
            errors=[error_detail(message=f"User with ID {user_id} not found")]
        )
    
    # Verificar se role existe
    role = get_role(db, role_update.role_id)
    if not role:
        return error_response(
            message="Role not found",
            status_code=status.HTTP_404_NOT_FOUND,
            errors=[error_detail(message=f"Role with ID {role_update.role_id} not found")]
        )
    
    # Atualizar role do usuário usando o serviço
    from app.schemas.user import UserUpdate
    user_update = UserUpdate(role_id=role_update.role_id)
    updated_user = update_user_service(db, user_id, user_update)
    
    if not updated_user:
        return error_response(
            message="Failed to update user role",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    return get_response(
        data=updated_user,
        message="User role updated successfully"
    )

