import datetime
from dataclasses import dataclass

from infrastructure.models.balance_models.models import Balance
from infrastructure.models.order_models.enums import OrderStatusEnum
from infrastructure.models.order_models.models import Order
from infrastructure.models.revenue_models.models import Revenue
from infrastructure.repositories.balance_repository import BalanceRepository
from infrastructure.repositories.order_repository import OrderRepository
from infrastructure.repositories.revenue_repository import RevenueRepository


@dataclass
class DBData:

    revenue_row: Revenue = None
    placed_orders: list[Order] = None
    filled_orders: list[Order] = None
    balance: Balance = None
    current_time: datetime = None


    async def update_revenue_row(self):

        self.revenue_row = await RevenueRepository.get_current_revenue_row()

    async def update_balance(self):

        self.balance = await BalanceRepository.get_balance()

    async def update_placed_orders(self):

        self.placed_orders = await OrderRepository.get_by_status(status=OrderStatusEnum.placed.value)

    async def update_filled_orders(self):

        self.filled_orders = await OrderRepository.get_by_status(status=OrderStatusEnum.filled.value)

    async def update_current_time(self):

        self.current_time = datetime.datetime.now()

    async def get_current_data(self):

        await self.update_revenue_row()
        await self.update_balance()
        await self.update_placed_orders()
        await self.update_filled_orders()
        await self.update_current_time()



DB_DATA = DBData()