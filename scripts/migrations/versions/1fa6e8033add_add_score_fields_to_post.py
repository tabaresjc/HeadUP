"""add score fields to Post

Revision ID: 1fa6e8033add
Revises:
Create Date: 2016-11-15 06:33:09.374000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1fa6e8033add'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('score',
                                     sa.Numeric(20, 7),
                                     default=0,
                                     server_default='0',
                                     nullable=False))
    op.create_index('idx_score', 'posts', ['score'])


def downgrade():
    try:
        op.drop_column('posts', 'score')
        op.drop_index('idx_score', 'posts')
    except Exception as e:
        pass
