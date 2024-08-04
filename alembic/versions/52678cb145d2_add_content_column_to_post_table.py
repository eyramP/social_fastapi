"""Add content column to post table

Revision ID: 52678cb145d2
Revises: efb347817ee1
Create Date: 2024-08-03 12:56:41.345290

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '52678cb145d2'
down_revision: Union[str, None] = 'efb347817ee1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "post", sa.Column("content", sa.String(), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("post", "content")
