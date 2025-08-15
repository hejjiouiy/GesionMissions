"""etat mission update

Revision ID: 2082f227c9f9
Revises: daa68dc35dc1
Create Date: 2025-06-17 17:09:34.159304
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2082f227c9f9'
down_revision: Union[str, None] = 'daa68dc35dc1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add 'CLOTUREE' to etatmission enum."""

    op.execute("ALTER TYPE gestion_missions.etatmission ADD VALUE IF NOT EXISTS 'CLOTUREE';")


def downgrade() -> None:
    """Downgrade schema - removing enum value is not directly supported in PostgreSQL."""
    # ⚠️ PostgreSQL does not support removing ENUM values directly.
    # If needed, you must recreate the enum type manually and reassign it.
    pass
