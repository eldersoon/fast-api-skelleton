from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Cria a engine do banco de dados
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,  # Log SQL queries em modo debug
)

# SessionLocal é uma factory para criar sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Dependency para obter a sessão do banco de dados.
    Usar com Depends(get_db) nas rotas.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

