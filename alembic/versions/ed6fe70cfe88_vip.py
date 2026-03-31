"""vip

Revision ID: ed6fe70cfe88
Revises: bb6356567fac
Create Date: 2026-03-31 10:55:33.056157

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed6fe70cfe88'
down_revision: Union[str, None] = 'bb6356567fac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('tenders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_vip', sa.Boolean(), nullable=True))

def downgrade() -> None:
    with op.batch_alter_table('tenders', schema=None) as batch_op:
        batch_op.drop_column('is_vip')
