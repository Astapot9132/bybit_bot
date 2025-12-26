from sqlalchemy import String, Integer, Float, SmallInteger, Boolean
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from cfg.db_settings import Model


class TradeSetting(Model):
    __tablename__ = 'trade_settings'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    revenue_percent: Mapped[float] = mapped_column(Float(), server_default='0', nullable=False)
    percent_of_revenue_to_keep_in_crypto: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default='0')
    percent_step_per_order: Mapped[float] = mapped_column(Float(), nullable=False)
    max_order_count: Mapped[int] = mapped_column(SmallInteger(), nullable=False)
    delay_between_requests_in_seconds: Mapped[int] = mapped_column(Integer(), server_default='60', nullable=False)
    percent_between_first_order_and_current_price: Mapped[float] = mapped_column(Float(), server_default='0', nullable=False)
    max_percent_between_first_order_and_current_price: Mapped[float] = mapped_column(Float(), nullable=False)
    trade_pair: Mapped[str] = mapped_column(String(64), nullable=False)
    power: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default='True')
