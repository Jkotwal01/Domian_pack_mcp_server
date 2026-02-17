"""Add metadata column to chat_sessions

Revision ID: add_chat_session_metadata
Revises: 
Create Date: 2026-02-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_chat_session_metadata'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade():
    """Add session_metadata JSONB column to chat_sessions table."""
    op.add_column(
        'chat_sessions',
        sa.Column('session_metadata', postgresql.JSONB(), nullable=False, server_default='{}')
    )


def downgrade():
    """Remove session_metadata column from chat_sessions table."""
    op.drop_column('chat_sessions', 'session_metadata')
