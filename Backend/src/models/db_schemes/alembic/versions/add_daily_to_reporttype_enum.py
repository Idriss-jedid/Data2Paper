"""add daily to reporttype enum

Revision ID: 2d8a3f8e4b5c
Revises: cdea4954c61b
Create Date: 2025-09-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2d8a3f8e4b5c'
down_revision = 'cdea4954c61b'
branch_labels = None
depends_on = None


def upgrade():
    # Add 'DAILY' to the reporttype enum
    op.execute("ALTER TYPE reporttype ADD VALUE 'DAILY'")


def downgrade():
    # Note: Removing values from enums is not supported in PostgreSQL
    # This is a placeholder for completeness
    pass