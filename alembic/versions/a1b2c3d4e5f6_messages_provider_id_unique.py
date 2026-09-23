"""Add partial unique index on messages.provider_message_id for inbound deduplication

Revision ID: a1b2c3d4e5f6
Revises: 3af4fc95d3f9
Create Date: 2026-09-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '3af4fc95d3f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Partial unique index: only non-empty provider_message_id values must be unique.
    # Empty string is the default for messages that have not yet received a provider ID.
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS "
        "ix_messages_provider_message_id_nonempty "
        "ON messages (provider_message_id) "
        "WHERE provider_message_id != ''"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_messages_provider_message_id_nonempty")
