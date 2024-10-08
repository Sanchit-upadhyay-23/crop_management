"""Add a column

Revision ID: 68a39b96276f
Revises: ecfe7815b679
Create Date: 2024-10-07 22:12:58.372269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68a39b96276f'
down_revision: Union[str, None] = 'ecfe7815b679'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('trace_inventory', sa.Column('category', sa.VARCHAR(length=64), nullable=True))


def downgrade() -> None:
    pass
