
from dataclasses import dataclass

from infrastructure.repositories.trade_repository import TradeSettingRepository


@dataclass
class TradeData:

    percent_to_keep_in_cryptocurrency_after_iteration: int = None
    percent_price_increase: float = None
    percent_step_per_order: float = None
    max_order_count: int = None
    delay_between_requests: int = None
    percent_between_first_order_and_current_price: float = None
    max_percent_between_first_order_and_current_price: float = None
    trade_pair: str = None
    power: bool = None
    commission: float = 0.2
    revenue_without_commission: float = None
    percent_revenue_usd_per_round: float = None
    percent_revenue_btc_per_round: float = None

    async def get_trade_settings(self):

        stg = await TradeSettingRepository.get_settings()

        self.percent_price_increase = stg.revenue_percent
        self.percent_to_keep_in_cryptocurrency_after_iteration = stg.percent_of_revenue_to_keep_in_crypto
        self.percent_step_per_order = stg.percent_step_per_order
        self.max_order_count = stg.max_order_count
        self.delay_between_requests = stg.delay_between_requests_in_seconds
        self.percent_between_first_order_and_current_price = stg.percent_between_first_order_and_current_price
        self.max_percent_between_first_order_and_current_price = stg.max_percent_between_first_order_and_current_price
        self.trade_pair = stg.trade_pair
        self.power = stg.power
        self.revenue_without_commission = self.percent_price_increase - self.commission
        self.percent_revenue_usd_per_round = ((100 - self.percent_to_keep_in_cryptocurrency_after_iteration)
                                              * self.revenue_without_commission / 100)
        self.percent_revenue_btc_per_round = (self.percent_to_keep_in_cryptocurrency_after_iteration
                                              * self.revenue_without_commission / 100)


TRADE_DATA = TradeData()