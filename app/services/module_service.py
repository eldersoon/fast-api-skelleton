from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.module import Module


def get_module(db: Session, module_id: int) -> Optional[Module]:
    """Busca um módulo por ID"""
    return db.query(Module).filter(Module.id == module_id).first()


def get_module_by_key(db: Session, key: str) -> Optional[Module]:
    """Busca um módulo por key"""
    return db.query(Module).filter(Module.key == key).first()


def get_modules(db: Session) -> List[Module]:
    """Lista todos os módulos"""
    return db.query(Module).all()

