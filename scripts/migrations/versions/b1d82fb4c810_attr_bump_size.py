"""attr_bump_size

Revision ID: b1d82fb4c810
Revises: 7d87ed1b0f63
Create Date: 2020-05-03 18:08:41.506487

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = 'b1d82fb4c810'
down_revision = '7d87ed1b0f63'
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column('categories', 'attr',
                    existing_type=mysql.LONGTEXT(),
                    nullable=True)
    op.alter_column('pictures', 'attr',
                    existing_type=mysql.LONGTEXT(),
                    nullable=True)
    op.alter_column('posts', 'attr',
                    existing_type=mysql.LONGTEXT(),
                    nullable=True)
    op.alter_column('users', 'attr',
                    existing_type=mysql.LONGTEXT(),
                    nullable=True)

def downgrade():
    op.alter_column('categories', 'attr',
                    existing_type=mysql.TEXT(),
                    nullable=True)
    op.alter_column('pictures', 'attr',
                    existing_type=mysql.TEXT(),
                    nullable=True)
    op.alter_column('posts', 'attr',
                    existing_type=mysql.TEXT(),
                    nullable=True)
    op.alter_column('users', 'attr',
                    existing_type=mysql.TEXT(),
                    nullable=True)
