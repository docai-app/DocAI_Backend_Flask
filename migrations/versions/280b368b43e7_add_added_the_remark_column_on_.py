"""Add: Added the remark column on documents_approval table.

Revision ID: 280b368b43e7
Revises: efa519933249
Create Date: 2022-07-08 17:34:16.336373

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '280b368b43e7'
down_revision = 'efa519933249'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('documents_approval', sa.Column('remark', sa.TEXT(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('documents_approval', 'remark')
    # ### end Alembic commands ###