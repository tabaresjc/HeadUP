"""create field to reset password in users table

Revision ID: 0d80f6e0ca0e
Revises: 94c1fbb83db2
Create Date: 2018-04-06 17:39:25.199000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d80f6e0ca0e'
down_revision = '94c1fbb83db2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('reset_password',
                                     sa.String(128),
                                     nullable=True))
    op.create_index('idx_reset_password',
        'users',
        ['reset_password'],
        unique=True)


def downgrade():
    try:
        op.drop_index('idx_reset_password', 'users')
        op.drop_column('users', 'reset_password')
    except Exception as e:
        pass
