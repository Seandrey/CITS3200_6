"""empty message

Revision ID: 56affa8e1d74
Revises: dfcae2a70176
Create Date: 2023-05-03 12:36:04.263526

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '56affa8e1d74'
down_revision = 'dfcae2a70176'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('activity_log', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_edited', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('activity_log', schema=None) as batch_op:
        batch_op.drop_column('is_edited')

    # ### end Alembic commands ###
