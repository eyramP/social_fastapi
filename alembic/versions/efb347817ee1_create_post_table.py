"""Create post table

Revision ID: efb347817ee1
Revises:
Create Date: 2024-08-03 04:23:11.275530

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'efb347817ee1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "post",
        sa.Column("id", UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4),
        sa.Column("title", sa.String(), nullable=False)
    )


def downgrade() -> None:
    op.drop_table("post")
