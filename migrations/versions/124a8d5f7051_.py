"""empty message

Revision ID: 124a8d5f7051
Revises: 
Create Date: 2021-11-12 13:38:18.031320

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.sqltypes import Boolean, LargeBinary


# revision identifiers, used by Alembic.
revision = '124a8d5f7051'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Message',
    sa.Column('message_id', sa.Integer(), autoincrement=True),
    sa.Column('text', sa.Unicode(), nullable=False),
    sa.Column('sender', sa.Integer(), nullable=False),
    sa.Column('recipient', sa.Integer(), nullable=True),
    sa.Column('media', sa.LargeBinary(), nullable=True),
    sa.Column('delivery_date', sa.DateTime(), nullable=True),
    sa.Column('is_draft', sa.Boolean(), default=True),
    sa.Column('is_delivered', sa.Boolean(), default=False),
    sa.Column('is_read', sa.Boolean(), default=False),
    # to take into account only to received message
    sa.Column('is_deleted', sa.Boolean(), default=False),
    sa.PrimaryKeyConstraint('message_id'),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Message')
    # ### end Alembic commands ###