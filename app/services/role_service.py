from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.module import Module
from app.models.role_module_permission import RoleModulePermission
from app.schemas.role import RoleCreate, RoleUpdate


def get_role(db: Session, role_id: int) -> Optional[Role]:
    """Busca um role por ID"""
    return db.query(Role).filter(Role.id == role_id).first()


def get_role_by_key(db: Session, key: str) -> Optional[Role]:
    """Busca um role por key"""
    return db.query(Role).filter(Role.key == key).first()


def get_roles(db: Session) -> List[Role]:
    """Lista todos os roles"""
    return db.query(Role).all()


def create_role(db: Session, role: RoleCreate) -> Role:
    """
    Cria um novo role.
    Roles criadas via API sempre têm is_system=False.
    """
    # Verificar se key já existe
    existing_role = get_role_by_key(db, role.key)
    if existing_role:
        raise ValueError(f"Role with key '{role.key}' already exists")
    
    db_role = Role(
        key=role.key,
        name=role.name,
        description=role.description,
        is_system=False  # Roles criadas via API nunca são de sistema
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def update_role(db: Session, role_id: int, role_update: RoleUpdate) -> Optional[Role]:
    """
    Atualiza um role.
    
    Regras:
    - Roles de sistema (is_system=True): não podem ter 'key' alterado
    - Roles customizadas: podem ter todos os campos alterados
    """
    db_role = get_role(db, role_id)
    if not db_role:
        return None
    
    update_data = role_update.model_dump(exclude_unset=True)
    
    # Se for role de sistema, não permite alterar 'key'
    if db_role.is_system and "key" in update_data:
        raise ValueError("Cannot change 'key' of a system role")
    
    # Verificar se nova key já existe (se estiver alterando)
    if "key" in update_data and update_data["key"] != db_role.key:
        existing_role = get_role_by_key(db, update_data["key"])
        if existing_role:
            raise ValueError(f"Role with key '{update_data['key']}' already exists")
    
    for field, value in update_data.items():
        setattr(db_role, field, value)
    
    db.commit()
    db.refresh(db_role)
    return db_role


def delete_role(db: Session, role_id: int) -> bool:
    """
    Deleta um role.
    
    Regras:
    - Roles de sistema não podem ser deletados
    - Roles com usuários vinculados não podem ser deletados
    
    Returns:
        True se deletado com sucesso, False caso contrário
    """
    db_role = get_role(db, role_id)
    if not db_role:
        return False
    
    # Não permite deletar roles de sistema
    if db_role.is_system:
        raise ValueError("Cannot delete a system role")
    
    # Verificar se há usuários vinculados
    from app.models.user import User
    users_count = db.query(User).filter(User.role_id == role_id).count()
    if users_count > 0:
        raise ValueError(f"Cannot delete role: {users_count} user(s) are associated with this role")
    
    db.delete(db_role)
    db.commit()
    return True

