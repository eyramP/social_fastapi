"""Add foreign key to post table

Revision ID: 5f7352a247b2
Revises: c324996f49e0
Create Date: 2024-08-03 17:47:14.517698

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '5f7352a247b2'
down_revision: Union[str, None] = 'c324996f49e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("post", sa.Column("owner_id", UUID(as_uuid=True), nullable=False))
    op.create_foreign_key(
        "post_user_fk",
        source_table="post",
        referent_table="users",
        local_cols=["owner_id"],
        remote_cols=["id"],
        ondelete="CASCADE"
    )


def downgrade() -> None:
    op.drop_constraint("post_user_fk", table_name="post")
    op.drop_column("post", "owner_id")
