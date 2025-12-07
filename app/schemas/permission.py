from pydantic import BaseModel
from typing import List, Optional
from app.schemas.role import Role
from app.schemas.module import Module


class PermissionBase(BaseModel):
    can_read: bool = False
    can_create: bool = False
    can_update: bool = False
    can_delete: bool = False


class PermissionUpdate(PermissionBase):
    pass


class RoleModulePermission(PermissionBase):
    id: int
    role_id: int
    module_id: int
    
    class Config:
        from_attributes = True


class ModulePermission(PermissionBase):
    """Permissão de um módulo com informações do módulo"""
    module_key: str
    module_name: str
    module_id: int


class RolePermissionMatrix(BaseModel):
    """Matriz de permissões de um role"""
    role: Role
    modules: List[ModulePermission]


class PermissionBulkUpdate(BaseModel):
    """Payload para atualização em massa de permissões"""
    permissions: List[dict]  # Lista de {module_key, can_read, can_create, can_update, can_delete}


class UserRoleUpdate(BaseModel):
    """Payload para atualizar role de um usuário"""
    role_id: int

