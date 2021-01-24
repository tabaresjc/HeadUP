"""user_sessions

Revision ID: 30bfdf5de9e7
Revises: b1d82fb4c810
Create Date: 2021-01-23 07:58:17.833406

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '30bfdf5de9e7'
down_revision = 'b1d82fb4c810'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('auth_token', sa.String(length=255), nullable=True),
        sa.Column('refreshed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], onupdate='NO ACTION', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB')

    op.create_index('idx_auth_token', 'user_sessions', ['auth_token'], unique=False)
    op.create_index('idx_user_id', 'user_sessions', ['user_id'], unique=False)


def downgrade():
    op.drop_table('user_sessions')
