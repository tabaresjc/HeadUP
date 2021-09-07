"""jwt

Revision ID: fd956a6ed3f1
Revises: 30bfdf5de9e7
Create Date: 2021-09-06 23:17:33.795149

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fd956a6ed3f1'
down_revision = '30bfdf5de9e7'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('jwt_auth',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('access_token', sa.String(length=127), nullable=True),
        sa.Column('user_token', sa.String(length=127), nullable=True),
        sa.Column('refreshed_at', sa.DateTime(), nullable=True),
        sa.Column('expired_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], onupdate='NO ACTION', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB')

    op.create_index('idx_access_token', 'jwt_auth', ['access_token'], unique=False)
    op.create_index('idx_user_token', 'jwt_auth', ['user_token'], unique=False)
    op.create_index('idx_access_user_tokens', 'jwt_auth', ['access_token', 'user_token'], unique=False)
    op.create_index('idx_user_id', 'jwt_auth', ['user_id'], unique=False)


def downgrade():
    op.drop_table('jwt_auth')
