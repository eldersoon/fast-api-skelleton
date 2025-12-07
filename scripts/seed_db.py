"""
Script para executar seeds no banco de dados.
Uso: python scripts/seed_db.py
"""
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.db.session import SessionLocal
from app.db.seeds import run_seeds


def main():
    """Executa os seeds"""
    db = SessionLocal()
    try:
        run_seeds(db)
    except Exception as e:
        print(f"✗ Error running seeds: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

