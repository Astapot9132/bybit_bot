from typing import Type

from sqlalchemy import select, func, update, delete, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import InstrumentedAttribute

from cfg import Model, SessionType


class SqlAlchemyRepository:
    """
    Общий класс для всех репозиториев, все методы из этого класса,
    реализуются в классах наследниках одинаково.

    В классе наследнике должен быть аргумент model
    """

    model: Model


    @classmethod
    async def get_max_id(cls, session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            query_select = func.max(cls.model.id)
            result = await session.execute(query_select)
            if result:
                result = result.scalars().first()
            return result

    @classmethod
    async def get_by_id(cls, id: int, select_fields: list[InstrumentedAttribute[int| str]] = None, session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            if not select_fields:
                select_fields = (cls.model, )
            query_select = select(*select_fields).where(cls.model.id == id) # noqa
            result = await session.execute(query_select)
            if result:
                result = result.scalars().first()
            return result

    @classmethod
    async def get_all(cls, select_fields: list[InstrumentedAttribute[int | str]] = None,
                      session_type: Type[SessionType] = SessionType.admin_session):
        model_fields = select_fields if select_fields else (cls.model,)

        async with session_type() as session:
            query_select = select(*model_fields)
            result = await session.execute(query_select)

            result = result.scalars().all()
            return result

    @classmethod
    async def get_all_ids(cls, session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            query_select = select(cls.model.id)
            result = await session.execute(query_select)
            if result:
                result = result.scalars().all()
            return result

    @classmethod
    async def get_count(cls, session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            try:
                query = select(func.count(cls.model.id))
                result = await session.execute(query)
                return result.scalar()
            except Exception as e:
                print(e)

    @classmethod
    async def add(cls, returning_fields: list[InstrumentedAttribute[int|str]] = None, session_type: Type[SessionType] = SessionType.admin_session, **kwargs):
        """
            Базовый метод добавления, в каждом индивидуальном классе
             должен быть переписан со своими аргументами
            :return: id созданной записи
          """
        async with session_type() as session:
            try:
                query_insert = insert(cls.model
                                      ).values(kwargs
                                               )

                if returning_fields:
                    query_insert = query_insert.returning(*returning_fields)

                result = await session.execute(query_insert)
                await session.commit()

                if returning_fields:
                    result = result.scalars().first()
                    return result

            except IntegrityError as e:
                print(e)

    @classmethod
    async def add_many(cls, values: list[dict], session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            try:
                query_insert = insert(cls.model).values(values)
                await session.execute(query_insert)
                await session.commit()
            except IntegrityError as e:
                print(e)


    @classmethod
    async def add_on_conflict_do_update_many(cls, values: list[dict],
                                             ignore_columns: set = None,
                                             constraint: str = None,
                                             conflict_target: list = None,
                                             session_type: Type[SessionType] = SessionType.admin_session,
                                             returning_fields: list[InstrumentedAttribute[int|str]] = None
                                             ):
        """
        метод INSERT ... ON CONFLICT ... DO UPDATE SET ...
        В случае отсутствия вводных параметров проверяет по id, не забывайте продумывать поля для конфликта перед использованием
        """
        async with session_type() as session:
            try:

                query_insert = insert(cls.model).values(values)
                if not ignore_columns:
                    ignore_columns = {'id'}

                if not constraint and not conflict_target:
                    conflict_target = ['id']

                update_dict = {
                    c.name: getattr(query_insert.excluded, c.name)
                    for c in cls.model.__table__.columns if c.name not in ignore_columns
                }

                query_on_conflict = query_insert.on_conflict_do_update(
                    index_elements=conflict_target,
                    constraint=constraint,
                    set_=update_dict
                )

                # если надо вернуть поля, добавляем их к запросу
                if returning_fields:
                    query_on_conflict = query_on_conflict.returning(*returning_fields)

                executed_query = await session.execute(query_on_conflict)
                await session.commit()

                if returning_fields:
                    result = executed_query.fetchall()
                    return result

            except IntegrityError as e:
                print(e)
            except Exception as e:
                print('Возникла другая ошибка ', e)

    @classmethod
    async def add_on_conflict_do_update_many_without_commit(cls, values: list[dict],
                                             session,
                                             ignore_columns: set = None,
                                             constraint: str = None,
                                             conflict_target: list = None,
                                             ):
        """
        метод INSERT ... ON CONFLICT ... DO UPDATE SET ...
        В случае отсутствия вводных параметров проверяет по id, не забывайте продумывать поля для конфликта перед использованием
        """
        try:

            query_insert = insert(cls.model).values(values)
            if not ignore_columns:
                ignore_columns = {'id'}

            if not constraint and not conflict_target:
                conflict_target = ['id']

            update_dict = {
                c.name: getattr(query_insert.excluded, c.name)
                for c in cls.model.__table__.columns if c.name not in ignore_columns
            }

            query_on_conflict = query_insert.on_conflict_do_update(
                index_elements=conflict_target,
                constraint=constraint,
                set_=update_dict
            )
            await session.execute(query_on_conflict)
        except IntegrityError as e:
            print(e)
        except Exception as e:
            print('Возникла другая ошибка ', e)


    @classmethod
    async def add_on_conflict_do_nothing_many(cls, values: list[dict],
                                            constraint: str = None,
                                            conflict_target: list = None,
                                            session_type: Type[SessionType] = SessionType.admin_session,
                                            returning_fields: list[InstrumentedAttribute[int|str]] = None,
                                              ):
        """
        Метод INSERT ... ON CONFLICT ... DO NOTHING
        В случае отсутствия вводных параметров проверяет по id, не забывайте продумывать поля для конфликта перед использованием
        """
        async with session_type() as session:
            try:
                query_insert = insert(cls.model).values(values)

                if not constraint and not conflict_target:
                    conflict_target = ['id']

                query_on_conflict = query_insert.on_conflict_do_nothing(
                    index_elements=conflict_target,
                    constraint=constraint
                )

                # если надо вернуть поля, добавляем их к запросу
                if returning_fields:
                    query_on_conflict = query_on_conflict.returning(*returning_fields)

                executed_query = await session.execute(query_on_conflict)
                await session.commit()

                if returning_fields:
                    result = executed_query.fetchall()
                    return result

            except IntegrityError as e:
                print(e)
            except Exception as e:
                print('Возникла другая ошибка ', e)


    @classmethod
    async def update_by_id(cls, id, fields: dict, session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            try:
                query_update = update(cls.model
                                      ).where(cls.model.id == id,
                                              ).values(**fields)
                await session.execute(query_update)
                await session.commit()
            except Exception as e:
                print(e)
                return e

    @classmethod
    async def delete_by_id(cls, id, session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            try:
                query_delete = delete(cls.model
                                      ).where(cls.model.id==id)
                await session.execute(query_delete)
                await session.commit()
            except Exception as e:
                print(e)


    @classmethod
    async def delete_all(cls, session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            try:
                query_delete = delete(cls.model)
                await session.execute(query_delete)
                await session.commit()
            except Exception as e:
                print(e)
                return e

    @classmethod
    async def get_max_updated_at(cls, session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            try:
                query_select = func.max(cls.model.updated_at)
                result = await session.execute(query_select)
                return result.scalars().first()
            except Exception as e:
                print(e)

    @classmethod
    async def change_autoincrement(cls, max_id_import, session_type: Type[SessionType] = SessionType.admin_session):
        async with session_type() as session:
            query = text(f"SELECT last_value FROM {cls.model.__tablename__}_id_seq")
            result = await session.execute(query)
            autoincrement_in_bd = result.scalars().first()
            if max_id_import > autoincrement_in_bd:
                print(f'Максимальный id был при импорте в {cls.model.__tablename__}: {max_id_import}, следующий меняем на {max_id_import + 1}')
                query_update = text(f"ALTER SEQUENCE {cls.model.__tablename__}_id_seq RESTART WITH {max_id_import + 1};")
                await session.execute(query_update)
                await session.commit()
                return
            print(f'Максимальный id был в базе данных {cls.model.__tablename__}: {autoincrement_in_bd}')
