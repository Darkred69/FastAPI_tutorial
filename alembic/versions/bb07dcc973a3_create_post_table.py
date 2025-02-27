"""create post table

Revision ID: bb07dcc973a3
Revises: 
Create Date: 2025-02-26 16:06:45.743920

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb07dcc973a3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('posts'
                    ,sa.Column('id', sa.Integer(), nullable = False, primary_key = True)
                    , sa.Column('title', sa.String(), nullable = False))
    pass


def downgrade() -> None:
    op.drop_table('posts')
    pass
