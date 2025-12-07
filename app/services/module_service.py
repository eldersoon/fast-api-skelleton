from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.module import Module
from app.core.modules_registry import MODULES_REGISTRY


def get_module(db: Session, module_id: int) -> Optional[Module]:
    """Busca um módulo por ID"""
    return db.query(Module).filter(Module.id == module_id).first()


def get_module_by_key(db: Session, key: str) -> Optional[Module]:
    """Busca um módulo por key"""
    return db.query(Module).filter(Module.key == key).first()


def get_modules(db: Session) -> List[Module]:
    """Lista todos os módulos"""
    return db.query(Module).all()


def sync_modules_from_registry(db: Session) -> None:
    """
    Sincroniza módulos do MODULES_REGISTRY com o banco de dados.
    Idempotente: cria módulos que não existem, atualiza os que já existem.
    """
    for module_data in MODULES_REGISTRY:
        existing_module = db.query(Module).filter(Module.key == module_data["key"]).first()
        
        if existing_module:
            # Atualizar name e description se necessário
            if (existing_module.name != module_data["name"] or 
                existing_module.description != module_data.get("description")):
                existing_module.name = module_data["name"]
                existing_module.description = module_data.get("description")
        else:
            # Criar novo módulo
            module = Module(
                key=module_data["key"],
                name=module_data["name"],
                description=module_data.get("description")
            )
            db.add(module)
    
    db.commit()
