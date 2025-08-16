"""add_user_settings_fields

Revision ID: 7a8844aab827
Revises: 
Create Date: 2025-08-14 17:36:34.273596
"""

from typing import Sequence, Union

from alembic_env import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '7a8844aab827'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем недостающие поля в user_settings
    with op.batch_alter_table("user_settings", schema=None) as batch_op:
        batch_op.add_column(sa.Column("topic", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("intensity", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("format", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("language", sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("user_settings", schema=None) as batch_op:
        batch_op.drop_column("language")
        batch_op.drop_column("format")
        batch_op.drop_column("intensity")
        batch_op.drop_column("topic")
