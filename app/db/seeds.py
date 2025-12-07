"""
Script de seed para popular dados iniciais do sistema.
Execute após rodar as migrations.
"""
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.module import Module


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
    """Cria os módulos iniciais do sistema"""
    modules_data = [
        {
            "key": "users",
            "name": "Usuários",
            "description": "Gerenciamento de usuários"
        },
        {
            "key": "access_control",
            "name": "Controle de Acesso",
            "description": "Gerenciar papéis e permissões"
        },
        {
            "key": "reports",
            "name": "Relatórios",
            "description": "Visualização de relatórios"
        },
        {
            "key": "inventory",
            "name": "Inventário",
            "description": "Gestão de itens/estoque"
        }
    ]
    
    for module_data in modules_data:
        existing_module = db.query(Module).filter(Module.key == module_data["key"]).first()
        if not existing_module:
            module = Module(**module_data)
            db.add(module)
    
    db.commit()
    print("✓ Modules seeded successfully")


def run_seeds(db: Session):
    """Executa todos os seeds"""
    print("Running seeds...")
    seed_roles(db)
    seed_modules(db)
    print("✓ All seeds completed successfully")

