from cfg.trade_data import TRADE_DATA
from infrastructure.models.order_models.enums import OrderStatusEnum
from infrastructure.repositories.order_repository import OrderRepository
from core.bybit_data import BYBIT_DATA
from core.db_data import DB_DATA
from core import buy, sell, cancel, get_open_orders_ids
from infrastructure.repositories.balance_repository import BalanceRepository
from infrastructure.repositories.revenue_repository import RevenueRepository


async def make_new_order_list_and_revenue_row():

    if DB_DATA.revenue_row:
        await RevenueRepository.finish_revenue_row(DB_DATA.revenue_row.id)

    print('Ордера отсутствуют, создаем новую сетку')

    await RevenueRepository.add(
        max_orders=TRADE_DATA.max_order_count,
        trade_pair=TRADE_DATA.trade_pair
    )

    await DB_DATA.update_revenue_row()

    await make_order_list()


async def make_order_list(orders_count: int = None, start_price: float = None):

    if not orders_count:
        orders_count = TRADE_DATA.max_order_count

    if not start_price:
        start_price = float(BYBIT_DATA.current_price)

    price_percent = 100 - TRADE_DATA.percent_between_first_order_and_current_price

    for num in range(orders_count):

        price_for_buy = start_price * price_percent / 100

        quantity_for_buy = float(DB_DATA.balance.current_sum // TRADE_DATA.max_order_count) / price_for_buy

        await buy(quantity_for_buy=quantity_for_buy, price_for_buy=price_for_buy,
                  revenue_id=DB_DATA.revenue_row.id)

        price_percent -= TRADE_DATA.percent_step_per_order


async def compare_orders_in_market_and_db() -> set:
    db_orders_ids = {order.external_id for order in DB_DATA.placed_orders}
    market_orders_external_ids = await get_open_orders_ids()

    diff = db_orders_ids.difference(market_orders_external_ids)
    if diff:
        print(f'Размещенные ордера в базе: {", ".join(db_orders_ids)}')
        print(f'Размещенные ордера на бирже: {", ".join(market_orders_external_ids)}')
    else:
        print('Состояние ордеров не изменилось')
    return diff

def check_sell_order_is_filled(order_difference_ids: set):

    for order_history in BYBIT_DATA.history:
        if order_history['orderId'] in order_difference_ids and order_history['side'] == 'Sell':
            return True


async def update_filled_order(order_history):
    print(f"Обновляем размещенный ордер {order_history['orderId']} на заполненный, а также обновляем текущую запись цикла")
    await OrderRepository.update_by_external_id(
        order_history['orderId'],
        fields={
            'status': OrderStatusEnum.filled.value,
            'order_executed_value': float(order_history['cumExecValue']),
            'order_fact_price': float(order_history['avgPrice']),
            'revenue_id': DB_DATA.revenue_row.id
        }
    )

    await DB_DATA.update_placed_orders()

async def update_sell_order_after_fill_buy_orders():
    await DB_DATA.update_revenue_row()
    sell_order = await OrderRepository.get_current_sell_order()

    if sell_order:
        await cancel(sell_order)

    await sell(
        quantity_for_sell=float(DB_DATA.revenue_row.current_quantity) - float(DB_DATA.revenue_row.revenue_btc),
        price_for_sell=max([float(DB_DATA.revenue_row.current_avg_price) * (1 + TRADE_DATA.percent_price_increase / 100), BYBIT_DATA.current_price * 0.999]),
        revenue_id=DB_DATA.revenue_row.id)


async def inspect_history_and_update_current_revenue_row_and_orders_conditions(diff_orders):
    for order_history in BYBIT_DATA.history:
        if order_history['orderId'] in diff_orders:
            if order_history['orderStatus'] == 'Filled':

                await update_filled_order(order_history)

            else:
                await OrderRepository.update_by_external_id(
                    order_history['orderId'],
                    fields={
                        'status': OrderStatusEnum.error.value,
                    }
                )
                raise Exception(f'Неизвестная ошибка. Ордер: {order_history}')

    await update_sell_order_after_fill_buy_orders()


async def update_current_data():
    await TRADE_DATA.get_trade_settings()
    if TRADE_DATA.power is False:
        return

    await DB_DATA.get_current_data()
    await BYBIT_DATA.get_current_data()


async def complete_sell_order_and_update_balance(sell_order):

    print(f'Ордер на продажу {sell_order.external_id} был заполнен')

    for order_history in BYBIT_DATA.history:

        if order_history['orderId'] == sell_order.external_id:

            print(f"Нашли ордер и проставляем статус '{OrderStatusEnum.completed.value}'")

            await OrderRepository.update_by_id(
                id=sell_order.id,
                fields={
                    'status': OrderStatusEnum.completed.value,
                    'order_executed_value': float(order_history['cumExecValue']),
                    'order_fact_price': float(order_history['avgPrice']),
                })

            await DB_DATA.update_placed_orders()

            break

    else:
        raise Exception(f'Не нашли в истории ордер с id {sell_order.external_id}')

    await BalanceRepository.update_balance(
        current_sum=float(DB_DATA.balance.current_sum) + float(DB_DATA.revenue_row.revenue_usd))


async def complete_filled_orders():
    for order in DB_DATA.filled_orders:
        await OrderRepository.update_by_id(order.id, fields={
            'status': OrderStatusEnum.completed.value
        })

async def finish_revenue_row_and_update_all_involved_orders():
    await cancel_placed_buy_orders()
    await complete_filled_orders()
    await RevenueRepository.finish_revenue_row(DB_DATA.revenue_row.id)


async def complete_old_revenue_row_and_start_new_with_old_placed_orders():
    await complete_filled_orders()

    await RevenueRepository.finish_revenue_row(DB_DATA.revenue_row.id)

    await RevenueRepository.add(
        max_orders=TRADE_DATA.max_order_count,
        trade_pair=TRADE_DATA.trade_pair
    )

    await DB_DATA.update_revenue_row()



async def cancel_placed_buy_orders():
    placed_orders = await OrderRepository.get_by_status_and_type(status=OrderStatusEnum.placed.value)
    for order in placed_orders:
        await cancel(order)


async def finish_revenue_row_update_all_orders_and_make_new_revenue_row_with_old_orders(buy_order_difference_ids):
    await complete_old_revenue_row_and_start_new_with_old_placed_orders()
    print('Создали новую итерацию')
    await inspect_history_and_update_current_revenue_row_and_orders_conditions(buy_order_difference_ids)
    await cancel_placed_buy_orders()

    if float(BYBIT_DATA.current_price) < float(DB_DATA.revenue_row.current_avg_price) * (
            1 + (TRADE_DATA.percent_price_increase / 100)):
        print('Поскольку планируемая цена на продажу выше текущей, то добавляем ордера к новой итерации')
        await make_order_list(
            orders_count=TRADE_DATA.max_order_count - DB_DATA.revenue_row.filled_orders,
            start_price=min(float(BYBIT_DATA.current_price), float(DB_DATA.revenue_row.current_avg_price))
        )


async def inspect_history_and_change_revenue_row_and_orders_conditions(order_difference_ids: set):
    sell_order = await OrderRepository.get_current_sell_order()
    await complete_sell_order_and_update_balance(sell_order)
    buy_order_difference_ids = order_difference_ids.difference({sell_order.external_id})

    if not buy_order_difference_ids:

        print(
            'Кроме продажного ордера, больше не было изменившихся ордеров, отменяем все и создаем новую итерацию')
        await finish_revenue_row_and_update_all_involved_orders()
        print('Успешное завершение круга без лишних ордеров на покупку')

    else:

        print(f'Среди измененных оказались также ордера на покупку: {", ".join(buy_order_difference_ids)}')
        await finish_revenue_row_update_all_orders_and_make_new_revenue_row_with_old_orders(buy_order_difference_ids)



async def handle_different_orders(order_difference_ids: set):
    print(f'Состояние ордеров {", ".join(order_difference_ids)} изменилось, читаем историю')
    sell_order_filled = check_sell_order_is_filled(order_difference_ids)

    if not sell_order_filled:

        print('Ордер на продажу не заполнен, оставляем прежний цикл')
        await inspect_history_and_update_current_revenue_row_and_orders_conditions(
            diff_orders=order_difference_ids
        )

    else:

        await inspect_history_and_change_revenue_row_and_orders_conditions(order_difference_ids)


async def condition_to_move_order_list():
    first_order_price = await OrderRepository.get_max_order_price()
    max_price_to_move_order_list = float(first_order_price) * (1 + (TRADE_DATA.max_percent_between_first_order_and_current_price / 100))

    return (
            not DB_DATA.revenue_row.filled_orders
            and BYBIT_DATA.current_price > max_price_to_move_order_list
    )


async def handle_if_find_order_difference_or_check_condition_to_move_order_list(order_difference_ids):
    print('Есть размещенные ордера, продолжаем текущую итерацию')

    if order_difference_ids:

        await handle_different_orders(order_difference_ids)

    else:

        if await condition_to_move_order_list():
            print(
                f'Цена ушла от 1 ордера дальше чем на {TRADE_DATA.max_percent_between_first_order_and_current_price} процентов, переносим сетку')
            await finish_revenue_row_and_update_all_involved_orders()
