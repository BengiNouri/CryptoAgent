"""create_prices_table

Revision ID: 62267c53d18d
Revises: 
Create Date: 2025-07-16 10:54:45.447436

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '62267c53d18d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'prices',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('coin_id', sa.Text, nullable=False),
        sa.Column('symbol', sa.Text, nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('price', sa.Numeric, nullable=False),
        sa.Column('market_cap', sa.Numeric, nullable=True),
        sa.Column('volume', sa.Numeric, nullable=True),
    )
    
    # Add indexes for better query performance
    op.create_index('idx_prices_symbol_date', 'prices', ['symbol', 'date'])
    op.create_index('idx_prices_coin_id_date', 'prices', ['coin_id', 'date'])


def downgrade() -> None:
    op.drop_index('idx_prices_coin_id_date', 'prices')
    op.drop_index('idx_prices_symbol_date', 'prices')
    op.drop_table('prices')