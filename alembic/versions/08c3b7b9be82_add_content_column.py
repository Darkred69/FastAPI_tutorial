"""add content column

Revision ID: 08c3b7b9be82
Revises: bb07dcc973a3
Create Date: 2025-02-26 16:13:15.466289

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08c3b7b9be82'
down_revision: Union[str, None] = 'bb07dcc973a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable = False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
