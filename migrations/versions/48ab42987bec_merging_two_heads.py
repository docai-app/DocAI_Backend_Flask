"""merging two heads

Revision ID: 48ab42987bec
Revises: e0432d936a75, e4ecf68030fa
Create Date: 2022-06-27 12:47:38.511715

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '48ab42987bec'
down_revision = ('e0432d936a75', 'e4ecf68030fa')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
