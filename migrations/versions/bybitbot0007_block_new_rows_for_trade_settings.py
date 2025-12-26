"""block new rows for trade settings

Revision ID: bybitbot0007
Revises: bybitbot0006
Create Date: 2025-02-09 16:10:43.779783

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from infrastructure.stored_procedures.trade_settings.trade_settings_check_rows_limit import \
    sql_register_store_proc_trade_settings_check_rows_limit, sql_drop_store_proc_trade_settings_check_rows_limit
from infrastructure.triggers.trade_settings.check_rows_limit import \
    sql_register_trigger_trade_settings_before_insert_check_rows_limit, \
    sql_drop_trigger_trade_settings_before_insert_check_rows

# revision identifiers, used by Alembic.
revision: str = 'bybitbot0007'
down_revision: Union[str, None] = 'bybitbot0006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(sql_register_store_proc_trade_settings_check_rows_limit())
    op.execute(sql_register_trigger_trade_settings_before_insert_check_rows_limit())


def downgrade() -> None:
    op.execute(sql_drop_trigger_trade_settings_before_insert_check_rows())
    op.execute(sql_drop_store_proc_trade_settings_check_rows_limit())
