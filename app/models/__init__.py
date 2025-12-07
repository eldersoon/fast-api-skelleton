# Importar todos os models aqui para garantir que sejam registrados no Base.metadata
from app.models.user import User  # noqa
from app.models.role import Role  # noqa
from app.models.module import Module  # noqa
from app.models.role_module_permission import RoleModulePermission  # noqa

__all__ = ["User", "Role", "Module", "RoleModulePermission"]

