"""add pilot_id to job

Revision ID: bb6356567fac
Revises: 31d519fa89af
Create Date: 2026-03-31 09:32:11.608775

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb6356567fac'
down_revision: Union[str, None] = '31d519fa89af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    try:
        with op.batch_alter_table('jobs', schema=None) as batch_op:
            batch_op.add_column(sa.Column('pilot_id', sa.BigInteger(), nullable=True))
            batch_op.create_foreign_key('fk_jobs_pilot_id_users', 'users', ['pilot_id'], ['telegram_id'])
    except Exception:
        pass

def downgrade() -> None:
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.drop_constraint('fk_jobs_pilot_id_users', type_='foreignkey')
        batch_op.drop_column('pilot_id')
