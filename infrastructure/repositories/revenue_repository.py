from typing import Type

from sqlalchemy import select, update

from cfg import SessionType
from cfg.trade_data import TRADE_DATA
from infrastructure.models.revenue_models.models import Revenue
from infrastructure.repositories.sqlalchemy_repository import SqlAlchemyRepository


class RevenueRepository(SqlAlchemyRepository):

    model = Revenue

    @classmethod
    async def get_current_revenue_row(cls, session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            query_select = select(cls.model).where(cls.model.finish == False, cls.model.trade_pair == TRADE_DATA.trade_pair)
            executed_query = await session.execute(query_select)
            result = executed_query.scalars().all()
            if result:
                if len(result) > 1:
                    raise Exception(f'В базе данных несколько записей с доходом по {TRADE_DATA.trade_pair}')
                else:
                    return result[0]

    @classmethod
    async def finish_revenue_row(cls, id, session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            try:
                query_update = update(cls.model
                                      ).where(cls.model.id == id,
                                              ).values(finish=True)
                await session.execute(query_update)
                await session.commit()
            except Exception as e:
                print(e)
                return e