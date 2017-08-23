"""create mutable columns encoded with JSON

Revision ID: e878b90e5a78
Revises: f6c1e07ef388
Create Date: 2017-08-23 13:46:03.426000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e878b90e5a78'
down_revision = 'f6c1e07ef388'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('attr', sa.dialects.mysql.LONGTEXT))
    op.add_column('pictures', sa.Column('attr', sa.dialects.mysql.LONGTEXT))
    op.add_column('users', sa.Column('attr', sa.dialects.mysql.LONGTEXT))
    op.add_column('categories', sa.Column('attr', sa.dialects.mysql.LONGTEXT))


def downgrade():
    op.drop_column('posts', 'attr')
    op.drop_column('pictures', 'attr')
    op.drop_column('users', 'attr')
    op.drop_column('categories', 'attr')
