"""b2g_tenders

Revision ID: ea370f4f23b8
Revises: 7447e3e6b5c0
Create Date: 2026-03-31 02:59:27.721009

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea370f4f23b8'
down_revision: Union[str, None] = '7447e3e6b5c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tenders", sa.Column("is_b2g", sa.Boolean(), server_default='0', nullable=False))
    op.add_column("tenders", sa.Column("b2g_status", sa.String(length=50), server_default="new", nullable=False))
    op.add_column("tenders", sa.Column("eis_fz", sa.String(length=50), nullable=True))
    op.add_column("tenders", sa.Column("customer_name", sa.String(length=255), nullable=True))
    op.add_column("tenders", sa.Column("b2g_url", sa.String(length=500), nullable=True))
    
    with op.batch_alter_table('tenders', schema=None) as batch_op:
        batch_op.alter_column('employer_id',
               existing_type=sa.BigInteger(),
               nullable=True)

def downgrade() -> None:
    pass
