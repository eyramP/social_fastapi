"""Add few remaining columns to post table

Revision ID: f1046d05378a
Revises: 5f7352a247b2
Create Date: 2024-08-03 18:25:15.825599

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1046d05378a'
down_revision: Union[str, None] = '5f7352a247b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("post", sa.Column("published", sa.Boolean(), nullable=False, server_default="True"),),
    op.add_column("post", sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),)


def downgrade() -> None:
    op.dro_column("post", "published")
    op.dro_column("post", "created_at")
