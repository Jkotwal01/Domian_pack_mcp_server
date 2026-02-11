"""Initial database migration - create all tables."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )
    op.create_index('ix_users_email', 'users', ['email'])
    
    # Create domain_configs table
    op.create_table(
        'domain_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('owner_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('version', sa.String(50), nullable=False, server_default='1.0.0'),
        sa.Column('config_json', postgresql.JSONB(), nullable=False),
        sa.Column('entity_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('relationship_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('extraction_pattern_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('key_term_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    op.create_index('ix_domain_configs_owner', 'domain_configs', ['owner_user_id'])
    op.execute("CREATE INDEX ix_domain_configs_json ON domain_configs USING GIN (config_json)")
    
    # Create session_status enum
    op.execute("CREATE TYPE session_status AS ENUM ('active', 'closed')")
    
    # Create chat_sessions table
    op.create_table(
        'chat_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('domain_config_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('domain_configs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.Enum('active', 'closed', name='session_status'), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('last_activity_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )
    op.create_index('ix_chat_sessions_user', 'chat_sessions', ['user_id'])
    op.create_index('ix_chat_sessions_domain', 'chat_sessions', ['domain_config_id'])
    
    # Create unique constraint for active sessions
    op.execute("""
        CREATE UNIQUE INDEX uq_user_domain_active_session 
        ON chat_sessions (user_id, domain_config_id, status) 
        WHERE status = 'active'
    """)
    
    # Create message_role enum
    op.execute("CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system')")
    
    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.Enum('user', 'assistant', 'system', name='message_role'), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )
    op.create_index('ix_chat_messages_session', 'chat_messages', ['session_id', 'created_at'])


def downgrade() -> None:
    op.drop_table('chat_messages')
    op.execute("DROP TYPE message_role")
    op.drop_table('chat_sessions')
    op.execute("DROP TYPE session_status")
    op.drop_table('domain_configs')
    op.drop_table('users')
