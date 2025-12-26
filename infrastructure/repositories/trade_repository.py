from typing import Type

from sqlalchemy import select

from cfg import SessionType
from infrastructure.models.trade_settings_models.models import TradeSetting
from infrastructure.repositories.sqlalchemy_repository import SqlAlchemyRepository


class TradeSettingRepository(SqlAlchemyRepository):

    model = TradeSetting

    @classmethod
    async def get_settings(cls, session_type: Type[SessionType] = SessionType.admin_session) -> TradeSetting:
        async with session_type() as session:
            query_select = select(cls.model)
            executed_query = await session.execute(query_select)
            result = executed_query.scalars().all()
            if result:
                if len(result) > 1:
                    raise Exception(f'В базе данных несколько записей с настройками')
                else:
                    return result[0]

            raise Exception('Не найдены настройки для торговли, заполните таблицу trade_settings')
