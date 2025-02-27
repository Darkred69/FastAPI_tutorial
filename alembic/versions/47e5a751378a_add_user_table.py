"""add user table

Revision ID: 47e5a751378a
Revises: 08c3b7b9be82
Create Date: 2025-02-26 16:20:33.801330

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '47e5a751378a'
down_revision: Union[str, None] = '08c3b7b9be82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users',
                  sa.Column('id', sa.Integer(), nullable=False),
                  sa.Column('email', sa.String(), nullable=False),
                  sa.Column('password', sa.String(), nullable=False),
                  sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
                  sa.PrimaryKeyConstraint('id'),
                  sa.UniqueConstraint('email')
                  )
    pass


def downgrade() -> None:
    op.drop_table('users')
    pass
