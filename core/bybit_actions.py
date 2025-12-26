import datetime

from cfg import CLIENT
from cfg.trade_data import TRADE_DATA
from infrastructure.models.order_models.enums import OrderStatusEnum, OrderTypeEnum
from infrastructure.models.order_models.models import Order
from infrastructure.repositories.order_repository import OrderRepository


async def buy(quantity_for_buy: float, price_for_buy: float, revenue_id: int):
    # Считаем, сколько можно купить

    decimals = str(quantity_for_buy).split('.')[1][:6]
    integer = str(quantity_for_buy).split('.')[0]
    real_sum_for_buy = f'{integer}.{decimals}'

    order = CLIENT.place_order(
        category="spot",
        symbol=TRADE_DATA.trade_pair,
        side="Buy",
        orderType="Limit",
        qty=real_sum_for_buy,
        price=round(price_for_buy, 1),
    )

    await OrderRepository.add(
        type=OrderTypeEnum.buy.value,
        external_id=order['result']['orderId'],
        external_order_link_id=order['result']['orderLinkId'],
        status=OrderStatusEnum.placed.value,
        order_trade_pair=TRADE_DATA.trade_pair,
        order_price=round(price_for_buy, 1),
        order_quantity=float(real_sum_for_buy),
        revenue_id=revenue_id
    )

    print(f"Создали ордер на покупку с id {order['result']['orderId']}")


async def sell(quantity_for_sell: float, price_for_sell: float, revenue_id: int):

    decimals = str(quantity_for_sell).split('.')[1][:6]
    integer = str(quantity_for_sell).split('.')[0]
    real_quantity_for_sell = f'{integer}.{decimals}'

    order = CLIENT.place_order(
        category="spot",
        symbol=TRADE_DATA.trade_pair,
        side="Sell",
        orderType="Limit",
        qty=real_quantity_for_sell,
        price=round(price_for_sell, 1),
    )

    await OrderRepository.add(
        type=OrderTypeEnum.sell.value,
        external_id=order['result']['orderId'],
        external_order_link_id=order['result']['orderLinkId'],
        status=OrderStatusEnum.placed.value,
        order_trade_pair=TRADE_DATA.trade_pair,
        order_price=round(price_for_sell, 1),
        order_quantity=float(real_quantity_for_sell),
        revenue_id=revenue_id
    )
    print(f"Создали ордер на продажу с id {order['result']['orderId']}")


async def cancel(order: Order):
    CLIENT.cancel_order(
        symbol=TRADE_DATA.trade_pair,
        order_id=order.external_id,
        category="spot"
    )

    await OrderRepository.update_by_id(order.id, fields={
        'status': OrderStatusEnum.cancelled.value
    })


async def get_open_orders_ids() -> set:
    open_orders_response = CLIENT.get_open_orders(category="spot", symbol=TRADE_DATA.trade_pair)
    open_orders_ids = {order['orderId'] for order in open_orders_response['result']['list']}

    return open_orders_ids

async def get_history_of_orders_from_date(start_datetime: datetime.datetime = None) -> list:
    """
    Особенность работы метода библиотеки pybit, что он возвращает историю
    только за 7 дней с выбранной даты либо за последние 7 дней
    """

    start_time_ms = int(start_datetime.timestamp() * 1000)
    history_response = CLIENT.get_order_history(category='spot', startTime=start_time_ms, symbol=TRADE_DATA.trade_pair, limit=100)
    clear_history_of_orders = history_response['result']['list']

    return clear_history_of_orders


async def get_current_price_of_trade_pair(trade_pair: str = None):
    if not trade_pair:
        trade_pair = TRADE_DATA.trade_pair
    tickers = CLIENT.get_tickers(category="spot", symbol=trade_pair)
    return float(tickers['result']['list'][0]['lastPrice'])
