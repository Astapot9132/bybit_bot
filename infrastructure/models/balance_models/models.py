from sqlalchemy import DECIMAL, SmallInteger
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from cfg.db_settings import Model


class Balance(Model):
    __tablename__ = 'balance'

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    current_sum: Mapped[float] = mapped_column(DECIMAL(10, 2))