from typing import Type

from sqlalchemy import select, update

from core.tools import round_down
from cfg.db_settings import SessionType
from infrastructure.models.balance_models.models import Balance
from infrastructure.repositories.sqlalchemy_repository import SqlAlchemyRepository


class BalanceRepository(SqlAlchemyRepository):

    model = Balance

    @classmethod
    async def get_balance(cls, session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            query_select = select(cls.model)
            result = await session.execute(query_select)
            if result:
                result = result.scalars().first()
            return result


    @classmethod
    async def update_balance(cls, current_sum: float, session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            try:
                query_update = update(cls.model
                                      ).values(current_sum=round_down(current_sum, 2))
                await session.execute(query_update)
                await session.commit()
            except Exception as e:
                print(e)
                return e