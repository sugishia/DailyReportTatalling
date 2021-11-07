"""empty message

Revision ID: a752b2ac9429
Revises: 52fa5e1bf98b
Create Date: 2021-11-06 21:58:59.705256

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a752b2ac9429'
down_revision = '52fa5e1bf98b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('branches', sa.Column('is_commissioner', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('branches', 'is_commissioner')
    # ### end Alembic commands ###
