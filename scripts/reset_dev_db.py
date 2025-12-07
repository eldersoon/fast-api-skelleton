"""
Script para resetar o banco de dados em ambiente de desenvolvimento.

Este script:
1. Limpa todas as tabelas do banco de dados
2. Executa todas as migrations
3. Executa os seeds

ATENÇÃO: Este script só deve ser executado em ambiente de desenvolvimento!

Uso:
    python scripts/reset_dev_db.py              # Com confirmação
    python scripts/reset_dev_db.py --yes         # Sem confirmação (útil para automação)
"""
import sys
import os
import argparse
from pathlib import Path

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import text, inspect, create_engine
from alembic import command
from alembic.config import Config

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.base import Base
from app.db.seeds import run_seeds

# Criar engine para operações de DDL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)


def check_environment():
    """Verifica se está em ambiente de desenvolvimento"""
    # Verificar variável de ambiente
    app_env = getattr(settings, 'APP_ENV', 'development').lower()
    
    # Verificar pelo nome do banco ou outras configurações
    db_url = str(settings.DATABASE_URL).lower()
    
    # Bloquear se for produção
    if app_env in ['production', 'prod'] or 'prod' in db_url or 'production' in db_url:
        print("❌ ERROR: This script should only be run in development environment!")
        print(f"   APP_ENV: {app_env}")
        print(f"   Database URL contains 'prod' or 'production'")
        sys.exit(1)
    
    print(f"✓ Environment check passed (APP_ENV: {app_env})")


def drop_all_tables():
    """Remove todas as tabelas do banco de dados"""
    print("\n🗑️  Dropping all tables...")
    
    db_url = str(engine.url)
    
    with engine.begin() as conn:
        # Obter lista de todas as tabelas
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            print("   No tables to drop")
            return
        
        # Desabilitar foreign key checks temporariamente (PostgreSQL)
        if 'postgresql' in db_url:
            conn.execute(text("SET session_replication_role = 'replica';"))
        
        # Dropar todas as tabelas
        for table in tables:
            print(f"   Dropping table: {table}")
            if 'postgresql' in db_url:
                conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE;'))
            elif 'sqlite' in db_url:
                conn.execute(text(f'DROP TABLE IF EXISTS "{table}";'))
            else:
                # Para outros bancos, usar SQL padrão
                conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE;'))
        
        # Reabilitar foreign key checks (PostgreSQL)
        if 'postgresql' in db_url:
            conn.execute(text("SET session_replication_role = 'origin';"))
    
    print("✓ All tables dropped successfully")


def run_migrations():
    """Executa todas as migrations do Alembic"""
    print("\n📦 Running migrations...")
    
    # Configurar Alembic
    alembic_cfg = Config(str(root_dir / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(root_dir / "alembic"))
    
    # Executar migrations até a versão mais recente
    try:
        command.upgrade(alembic_cfg, "head")
        print("✓ Migrations executed successfully")
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        raise


def run_seeds_script():
    """Executa os seeds do banco de dados"""
    print("\n🌱 Running seeds...")
    
    db = SessionLocal()
    try:
        run_seeds(db)
        print("✓ Seeds executed successfully")
    except Exception as e:
        print(f"❌ Error running seeds: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Função principal"""
    # Parse de argumentos
    parser = argparse.ArgumentParser(description='Reset database in development environment')
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Skip confirmation prompt'
    )
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔄 Database Reset Script - Development Environment")
    print("=" * 60)
    
    # Verificar ambiente
    check_environment()
    
    # Confirmar ação (a menos que --yes seja passado)
    if not args.yes:
        print("\n⚠️  WARNING: This will DELETE ALL DATA in the database!")
        response = input("   Are you sure you want to continue? (yes/no): ")
        
        if response.lower() not in ['yes', 'y']:
            print("\n❌ Operation cancelled")
            sys.exit(0)
    else:
        print("\n⚠️  WARNING: This will DELETE ALL DATA in the database!")
        print("   Proceeding without confirmation (--yes flag used)")
    
    try:
        # 1. Dropar todas as tabelas
        drop_all_tables()
        
        # 2. Executar migrations
        run_migrations()
        
        # 3. Executar seeds
        run_seeds_script()
        
        print("\n" + "=" * 60)
        print("✅ Database reset completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ ERROR: Database reset failed!")
        print(f"   {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()

