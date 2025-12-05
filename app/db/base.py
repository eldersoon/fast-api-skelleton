from sqlalchemy.ext.declarative import declarative_base

# Base para todos os models
Base = declarative_base()


# Importar todos os models aqui para que o Alembic possa encontrá-los
from app.models.user import User  # noqa


