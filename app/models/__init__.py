# Importar todos os models aqui para garantir que sejam registrados no Base.metadata
from app.models.user import User  # noqa

__all__ = ["User"]

