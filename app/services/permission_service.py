from typing import List, Dict
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.module import Module
from app.models.role_module_permission import RoleModulePermission
from app.schemas.permission import PermissionUpdate, ModulePermission


def get_role_permissions(db: Session, role_id: int) -> List[RoleModulePermission]:
    """Busca todas as permissões de um role"""
    return db.query(RoleModulePermission).filter(
        RoleModulePermission.role_id == role_id
    ).all()


def get_role_permission_matrix(db: Session, role_id: int) -> Dict:
    """
    Retorna a matriz de permissões de um role.
    
    Returns:
        {
            "role": Role,
            "modules": List[ModulePermission]
        }
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        return None
    
    # Buscar todos os módulos
    modules = db.query(Module).all()
    
    # Buscar permissões existentes
    permissions = {
        perm.module_id: perm
        for perm in db.query(RoleModulePermission).filter(
            RoleModulePermission.role_id == role_id
        ).all()
    }
    
    # Montar lista de permissões por módulo
    module_permissions = []
    for module in modules:
        perm = permissions.get(module.id)
        module_permissions.append({
            "module_key": module.key,
            "module_name": module.name,
            "module_id": module.id,
            "can_read": perm.can_read if perm else False,
            "can_create": perm.can_create if perm else False,
            "can_update": perm.can_update if perm else False,
            "can_delete": perm.can_delete if perm else False,
        })
    
    return {
        "role": role,
        "modules": module_permissions
    }


def update_role_permissions(
    db: Session,
    role_id: int,
    permissions_data: List[Dict]
) -> bool:
    """
    Atualiza permissões de um role.
    
    Args:
        db: Sessão do banco
        role_id: ID do role
        permissions_data: Lista de dicts com {module_key, can_read, can_create, can_update, can_delete}
    
    Returns:
        True se sucesso, False se role não encontrado
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        return False
    
    # Para cada permissão no payload
    for perm_data in permissions_data:
        module_key = perm_data.get("module_key")
        if not module_key:
            continue
        
        # Buscar módulo
        module = db.query(Module).filter(Module.key == module_key).first()
        if not module:
            continue
        
        # Buscar ou criar permissão
        permission = db.query(RoleModulePermission).filter(
            RoleModulePermission.role_id == role_id,
            RoleModulePermission.module_id == module.id
        ).first()
        
        if not permission:
            permission = RoleModulePermission(
                role_id=role_id,
                module_id=module.id,
                can_read=perm_data.get("can_read", False),
                can_create=perm_data.get("can_create", False),
                can_update=perm_data.get("can_update", False),
                can_delete=perm_data.get("can_delete", False),
            )
            db.add(permission)
        else:
            permission.can_read = perm_data.get("can_read", False)
            permission.can_create = perm_data.get("can_create", False)
            permission.can_update = perm_data.get("can_update", False)
            permission.can_delete = perm_data.get("can_delete", False)
    
    db.commit()
    return True

