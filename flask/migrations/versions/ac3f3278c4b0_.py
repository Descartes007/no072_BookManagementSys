"""empty message

Revision ID: ac3f3278c4b0
Revises: 58858575313f
Create Date: 2024-03-14 09:31:15.820954

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac3f3278c4b0'
down_revision = '58858575313f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('audit',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('op_time', sa.DateTime(), nullable=True),
    sa.Column('op_ip', sa.String(length=15), nullable=False),
    sa.Column('op_user', sa.String(length=32), nullable=False),
    sa.Column('op_module', sa.String(length=32), nullable=False),
    sa.Column('op_event', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('audit')
    # ### end Alembic commands ###