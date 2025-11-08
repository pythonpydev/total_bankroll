"""Add performance indexes for common queries

Revision ID: 1e063a8cc9f8
Revises: e9c441c44865
Create Date: 2025-11-08 15:49:21.489407

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1e063a8cc9f8'
down_revision = 'e9c441c44865'
branch_labels = None
depends_on = None


def upgrade():
    # Add composite indexes to optimize common queries
    # These indexes improve performance for user-specific time-series queries
    
    # Index for site_history queries (user_id, recorded_at)
    with op.batch_alter_table('site_history', schema=None) as batch_op:
        batch_op.create_index('idx_site_history_user_recorded', ['user_id', 'recorded_at'])
    
    # Index for asset_history queries (user_id, recorded_at)
    with op.batch_alter_table('asset_history', schema=None) as batch_op:
        batch_op.create_index('idx_asset_history_user_recorded', ['user_id', 'recorded_at'])
    
    # Index for deposits queries (user_id, date)
    with op.batch_alter_table('deposits', schema=None) as batch_op:
        batch_op.create_index('idx_deposits_user_date', ['user_id', 'date'])
    
    # Index for drawings queries (user_id, date)
    with op.batch_alter_table('drawings', schema=None) as batch_op:
        batch_op.create_index('idx_drawings_user_date', ['user_id', 'date'])


def downgrade():
    # Remove the indexes if we need to rollback
    
    with op.batch_alter_table('drawings', schema=None) as batch_op:
        batch_op.drop_index('idx_drawings_user_date')
    
    with op.batch_alter_table('deposits', schema=None) as batch_op:
        batch_op.drop_index('idx_deposits_user_date')
    
    with op.batch_alter_table('asset_history', schema=None) as batch_op:
        batch_op.drop_index('idx_asset_history_user_recorded')
    
    with op.batch_alter_table('site_history', schema=None) as batch_op:
        batch_op.drop_index('idx_site_history_user_recorded')

