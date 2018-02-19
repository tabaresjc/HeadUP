"""Add language column to posts

Revision ID: 94c1fbb83db2
Revises: e878b90e5a78
Create Date: 2018-02-19 17:31:08.993000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94c1fbb83db2'
down_revision = 'e878b90e5a78'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('lang',
                                     sa.String(4),
                                     server_default='en',
                                     nullable=True))
    op.create_index('idx_lang', 'posts', ['lang'])


def downgrade():
    op.drop_index('idx_lang', 'posts')
    op.drop_column('posts', 'lang')
