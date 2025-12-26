import datetime
from dataclasses import dataclass

from core.bybit_actions import get_history_of_orders_from_date, get_current_price_of_trade_pair


@dataclass
class BybitData:

    current_price: float = None
    history: list = None
    history_search_period: int = 14

    async def get_order_history_by_period(self):

        delta = 7
        self.history = []

        while delta < self.history_search_period:
            start_datetime = datetime.datetime.now() - datetime.timedelta(days=delta)
            history = await get_history_of_orders_from_date(start_datetime)
            self.history += history
            delta += 6



    async def update_current_price(self):

        self.current_price = await get_current_price_of_trade_pair()


    async def get_current_data(self):

        await self.update_current_price()
        await self.get_order_history_by_period()


BYBIT_DATA = BybitData()