"""add status to posts

Revision ID: f6c1e07ef388
Revises: 1fa6e8033add
Create Date: 2017-05-11 00:13:17.657110

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6c1e07ef388'
down_revision = '1fa6e8033add'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('status',
                                     sa.Integer,
                                     default=1,
                                     server_default='1',
                                     nullable=False))

    op.create_index('idx_status', 'posts', ['status'])


def downgrade():
    try:
        op.drop_column('posts', 'status')
        op.drop_index('idx_status', 'status')
    except Exception as e:
        pass
