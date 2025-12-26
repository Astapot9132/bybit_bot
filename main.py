import asyncio
import time

from core import *


async def main():

    while True:

        await update_current_data()

        if TRADE_DATA.power:

            print(f'Цена на {datetime.datetime.now().replace(microsecond=0)} составляет {BYBIT_DATA.current_price}')

            if not DB_DATA.placed_orders and not DB_DATA.filled_orders:

                await make_new_order_list_and_revenue_row()

            else:

                order_difference_ids = await compare_orders_in_market_and_db()

                await handle_if_find_order_difference_or_check_condition_to_move_order_list(order_difference_ids)

        time.sleep(TRADE_DATA.delay_between_requests)



if __name__ == "__main__":

    asyncio.run(main())
