"""
Script de seed para popular dados iniciais do sistema.
Execute após rodar as migrations.
"""
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.module import Module
from app.core.modules_registry import MODULES_REGISTRY


def seed_roles(db: Session):
    """Cria os roles iniciais do sistema"""
    roles_data = [
        {
            "key": "SUPER_ADMIN",
            "name": "Super Administrador",
            "description": "Acesso total ao sistema",
            "is_system": True
        },
        {
            "key": "ADMIN",
            "name": "Administrador",
            "description": "Acesso amplo ao sistema",
            "is_system": False
        },
        {
            "key": "USER",
            "name": "Usuário",
            "description": "Usuário comum",
            "is_system": False
        }
    ]
    
    for role_data in roles_data:
        existing_role = db.query(Role).filter(Role.key == role_data["key"]).first()
        if not existing_role:
            role = Role(**role_data)
            db.add(role)
    
    db.commit()
    print("✓ Roles seeded successfully")


def seed_modules(db: Session):
    """
    Sincroniza módulos do MODULES_REGISTRY com o banco de dados.
    Usa INSERT ... ON CONFLICT DO UPDATE para ser idempotente.
    """
    for module_data in MODULES_REGISTRY:
        # Verificar se módulo já existe
        existing_module = db.query(Module).filter(Module.key == module_data["key"]).first()
        
        if existing_module:
            # Atualizar name e description se necessário
            if (existing_module.name != module_data["name"] or 
                existing_module.description != module_data.get("description")):
                existing_module.name = module_data["name"]
                existing_module.description = module_data.get("description")
                db.commit()
        else:
            # Criar novo módulo
            module = Module(
                key=module_data["key"],
                name=module_data["name"],
                description=module_data.get("description")
            )
            db.add(module)
            db.commit()
    
    print("✓ Modules synchronized successfully")


def run_seeds(db: Session):
    """Executa todos os seeds"""
    print("Running seeds...")
    seed_roles(db)
    seed_modules(db)
    print("✓ All seeds completed successfully")

