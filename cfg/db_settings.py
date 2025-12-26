from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from cfg import POSTGRES_LOGIN, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_NAME

DB_URL = f"postgresql+asyncpg://{POSTGRES_LOGIN}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_NAME}"

DB_URL_SYNC = f"postgresql+psycopg2://{POSTGRES_LOGIN}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_NAME}"

engine = create_async_engine(
    DB_URL
)
admin_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

sync_admin_engine = create_engine(DB_URL_SYNC)
sync_admin_session = sessionmaker(bind=sync_admin_engine)


class Model(DeclarativeBase):
    pass


class SessionType:

    admin_session = admin_session