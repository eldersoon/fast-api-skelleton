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
    """Cria um novo role"""
    db_role = Role(
        key=role.key,
        name=role.name,
        description=role.description,
        is_system=role.is_system
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def update_role(db: Session, role_id: int, role_update: RoleUpdate) -> Optional[Role]:
    """Atualiza um role"""
    db_role = get_role(db, role_id)
    if not db_role:
        return None
    
    # Não permite atualizar roles do sistema
    if db_role.is_system:
        return None
    
    update_data = role_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_role, field, value)
    
    db.commit()
    db.refresh(db_role)
    return db_role

