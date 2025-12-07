"""add_rbac_tables_roles_modules_permissions

Revision ID: 4680038ade23
Revises: 1ca43c6c0e89
Create Date: 2025-12-05 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4680038ade23'
down_revision = '1ca43c6c0e89'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Criar tabela roles
    op.create_table('roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('is_system', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    op.create_index(op.f('ix_roles_key'), 'roles', ['key'], unique=True)
    
    # Criar tabela modules
    op.create_table('modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_modules_id'), 'modules', ['id'], unique=False)
    op.create_index(op.f('ix_modules_key'), 'modules', ['key'], unique=True)
    
    # Criar tabela role_module_permissions
    op.create_table('role_module_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('can_read', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('can_create', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('can_update', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('can_delete', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role_id', 'module_id', name='uq_role_module')
    )
    op.create_index(op.f('ix_role_module_permissions_id'), 'role_module_permissions', ['id'], unique=False)
    
    # Adicionar role_id na tabela users
    op.add_column('users', sa.Column('role_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_users_role_id', 'users', 'roles', ['role_id'], ['id'])


def downgrade() -> None:
    # Remover role_id da tabela users
    op.drop_constraint('fk_users_role_id', 'users', type_='foreignkey')
    op.drop_column('users', 'role_id')
    
    # Remover tabela role_module_permissions
    op.drop_index(op.f('ix_role_module_permissions_id'), table_name='role_module_permissions')
    op.drop_table('role_module_permissions')
    
    # Remover tabela modules
    op.drop_index(op.f('ix_modules_key'), table_name='modules')
    op.drop_index(op.f('ix_modules_id'), table_name='modules')
    op.drop_table('modules')
    
    # Remover tabela roles
    op.drop_index(op.f('ix_roles_key'), table_name='roles')
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.drop_table('roles')

