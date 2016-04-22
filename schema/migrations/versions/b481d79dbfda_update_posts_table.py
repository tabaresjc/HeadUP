"""update Posts table

Revision ID: b481d79dbfda
Revises:
Create Date: 2016-04-22 17:02:25.366000

"""

# revision identifiers, used by Alembic.
revision = 'b481d79dbfda'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('posts', sa.Column('extra_body', sa.Text))
    op.add_column('posts', sa.Column('is_anonymous', sa.SmallInteger))


def downgrade():
    op.drop_column('posts', 'extra_body')
    op.drop_column('posts', 'is_anonymous')
