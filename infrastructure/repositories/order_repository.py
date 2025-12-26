from typing import Type

from sqlalchemy import select, update, func

from cfg.db_settings import SessionType
from cfg.trade_data import TRADE_DATA
from infrastructure.models.order_models.enums import OrderTypeEnum, OrderStatusEnum
from infrastructure.models.order_models.models import Order
from infrastructure.repositories.sqlalchemy_repository import SqlAlchemyRepository


class OrderRepository(SqlAlchemyRepository):

    model = Order


    @classmethod
    async def get_current_sell_order(cls, session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            query_select = select(cls.model).where(cls.model.type == OrderTypeEnum.sell.value, cls.model.order_trade_pair == TRADE_DATA.trade_pair, cls.model.status == OrderStatusEnum.placed.value)
            result = await session.execute(query_select)
            if result:
                result = result.scalars().first()
            return result


    @classmethod
    async def get_by_external_id(cls, external_id, session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            query_select = select(cls.model).where(cls.model.external_id == external_id)
            result = await session.execute(query_select)
            if result:
                result = result.scalars().first()
            return result

    @classmethod
    async def get_max_order_price(cls, session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            query_select = select(func.max(cls.model.order_price)).where(cls.model.status.in_([OrderStatusEnum.placed, OrderStatusEnum.filled]))
            result = await session.execute(query_select)
            if result:
                result = result.scalars().first()
            return result

    @classmethod
    async def get_by_status(cls, status, session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            query_select = select(cls.model).where(cls.model.status == status, cls.model.order_trade_pair == TRADE_DATA.trade_pair)
            result = await session.execute(query_select)
            if result:
                result = result.scalars().all()
            return result

    @classmethod
    async def get_by_status_and_type(cls, status, type=OrderTypeEnum.buy.value, session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            query_select = select(cls.model).where(cls.model.status == status, cls.model.type==type, cls.model.order_trade_pair == TRADE_DATA.trade_pair)
            result = await session.execute(query_select)
            if result:
                result = result.scalars().all()
            return result

    @classmethod
    async def get_work_orders(cls, session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            query_select = select(cls.model).where(cls.model.status.in_([OrderStatusEnum.placed.value, OrderStatusEnum.filled.value]),  cls.model.order_trade_pair == TRADE_DATA.trade_pair,)
            result = await session.execute(query_select)
            if result:
                result = result.scalars().all()
            return result

    @classmethod
    async def update_by_external_id(cls, external_id, fields: dict, session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            try:
                query_update = update(cls.model
                                      ).where(cls.model.external_id == external_id,
                                              ).values(**fields)
                await session.execute(query_update)
                await session.commit()
            except Exception as e:
                print(e)
                return e
