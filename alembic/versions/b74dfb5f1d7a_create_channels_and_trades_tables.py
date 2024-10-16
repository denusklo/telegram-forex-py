"""Create channels and trades tables

Revision ID: b74dfb5f1d7a
Revises: 
Create Date: 2024-10-17 01:38:58.357436

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b74dfb5f1d7a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('channels',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('channel_id', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_channels_channel_id'), 'channels', ['channel_id'], unique=True)
    op.create_index(op.f('ix_channels_id'), 'channels', ['id'], unique=False)
    op.create_table('trades',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('action', sa.String(), nullable=True),
    sa.Column('pair', sa.String(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('sl', sa.Float(), nullable=True),
    sa.Column('tp', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trades_id'), 'trades', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_trades_id'), table_name='trades')
    op.drop_table('trades')
    op.drop_index(op.f('ix_channels_id'), table_name='channels')
    op.drop_index(op.f('ix_channels_channel_id'), table_name='channels')
    op.drop_table('channels')
    # ### end Alembic commands ###
