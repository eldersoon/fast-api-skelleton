"""add_can_access_system_to_users

Revision ID: bf249221ddb0
Revises: 4680038ade23
Create Date: 2025-12-05 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf249221ddb0'
down_revision = '4680038ade23'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adicionar coluna can_access_system na tabela users
    op.add_column('users', sa.Column('can_access_system', sa.Boolean(), server_default=sa.text('true'), nullable=True))


def downgrade() -> None:
    # Remover coluna can_access_system da tabela users
    op.drop_column('users', 'can_access_system')

