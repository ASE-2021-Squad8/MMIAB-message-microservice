"""empty message

Revision ID: ae7641612e44
Revises: 
Create Date: 2021-12-08 09:45:56.640046

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae7641612e44'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Message',
    sa.Column('message_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('text', sa.String(), nullable=True),
    sa.Column('delivery_date', sa.DateTime(), nullable=True),
    sa.Column('sender', sa.Integer(), nullable=True),
    sa.Column('recipient', sa.Integer(), nullable=True),
    sa.Column('media', sa.LargeBinary(), nullable=True),
    sa.Column('is_draft', sa.Boolean(), nullable=True),
    sa.Column('is_delivered', sa.Boolean(), nullable=True),
    sa.Column('is_read', sa.Boolean(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('message_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Message')
    # ### end Alembic commands ###
