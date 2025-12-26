import datetime

from sqlalchemy import DECIMAL, Boolean, String, DateTime, func, Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from cfg.db_settings import Model


class Revenue(Model):
    __tablename__ = 'revenue'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filled_orders: Mapped[int] = mapped_column(Integer, server_default='0', nullable=False)
    max_orders: Mapped[int] = mapped_column(Integer, nullable=False)
    revenue_usd: Mapped[float] = mapped_column(DECIMAL(10, 6), server_default='0', nullable=True)
    revenue_btc: Mapped[float] = mapped_column(DECIMAL(10, 6), server_default='0', nullable=True)
    current_avg_price: Mapped[float] = mapped_column(DECIMAL(10, 2), server_default='0', nullable=True)
    current_quantity: Mapped[float] = mapped_column(DECIMAL(10, 6), server_default='0', nullable=True)
    finish: Mapped[bool] = mapped_column(Boolean, server_default='False')
    created_at: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now())
    trade_pair: Mapped[str] = mapped_column(String(64), nullable=True)