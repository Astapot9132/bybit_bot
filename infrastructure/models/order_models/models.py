import datetime

from sqlalchemy import DECIMAL, String, DateTime, func, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from cfg.db_settings import Model
from infrastructure.models.order_models.enums import OrderTypeEnum, OrderStatusEnum


class Order(Model):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(ENUM(OrderTypeEnum, name='order_type_enum', create_type=False), nullable=False)
    external_id: Mapped[str] = mapped_column(String(64), nullable=False)
    external_order_link_id: Mapped[str] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(ENUM(OrderStatusEnum, name='order_status_enum', create_type=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now())
    order_trade_pair: Mapped[str] = mapped_column(String(64), nullable=False)
    order_type: Mapped[str] = mapped_column(String(64), nullable=False, server_default='Limit')
    order_price: Mapped[float] = mapped_column(DECIMAL(12,2), nullable=False)
    order_quantity: Mapped[float] = mapped_column(DECIMAL(10,6), nullable=False)
    order_executed_value: Mapped[float] = mapped_column(Float(), nullable=True) # сколько фактически заплатили
    order_fact_price: Mapped[str] = mapped_column(Float(), nullable=True) # цена по ордеру от bybit
    revenue_id: Mapped[int] = mapped_column(ForeignKey('revenue.id', ondelete='NO ACTION'), nullable=False)



