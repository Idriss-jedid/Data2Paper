"""Add OAuth fields to user table

Revision ID: oauth_fields_2024
Revises: 
Create Date: 2024-01-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'oauth_fields_2024'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add OAuth-related columns to users table"""
    # Add new columns
    op.add_column('users', sa.Column('is_oauth_user', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('google_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('github_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('apple_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('first_name', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('username', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.String(500), nullable=True))
    
    # Create unique indexes for OAuth IDs
    op.create_index('ix_users_google_id', 'users', ['google_id'], unique=True)
    op.create_index('ix_users_github_id', 'users', ['github_id'], unique=True)
    op.create_index('ix_users_apple_id', 'users', ['apple_id'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    
    # Make password_hash nullable for OAuth users
    op.alter_column('users', 'password_hash', nullable=True)


def downgrade():
    """Remove OAuth-related columns from users table"""
    # Drop indexes
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_apple_id', table_name='users')
    op.drop_index('ix_users_github_id', table_name='users')
    op.drop_index('ix_users_google_id', table_name='users')
    
    # Drop columns
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'username')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'apple_id')
    op.drop_column('users', 'github_id')
    op.drop_column('users', 'google_id')
    op.drop_column('users', 'is_oauth_user')
    
    # Make password_hash not nullable again
    op.alter_column('users', 'password_hash', nullable=False)
