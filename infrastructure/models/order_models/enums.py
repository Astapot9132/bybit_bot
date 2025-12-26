from enum import Enum


class OrderTypeEnum(Enum):

    buy = 'buy'
    sell = 'sell'


class OrderStatusEnum(Enum):

    placed = 'placed'
    cancelled = 'cancelled'
    error = 'error'
    filled = 'filled'
    completed = 'completed'