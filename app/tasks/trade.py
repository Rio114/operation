import time

import yaml
from app.config import Config
from app.entities.candle import QuoteCurrentCandleModel
from app.entities.transaction import OpenOrderModel
from app.infra.api.candle import Candle
from app.infra.api.transaction import Transaction
from app.logic.ichimoku_method import IchimokuMethod
from app.logic.ichimoku_method_dynamic_stop import IchimokuMethodDynamicStop
from app.tasks import get_module_logger


def trade(
    loaded_logic,
    instrument: str,
    transaction_client: Transaction,
    quote_client: Candle,
    position_units,
    logic_params,
    granularity="M15",
):
    logger = get_module_logger(__name__)
    config = Config()
    units = config.UNITS

    logic = loaded_logic(logic_params[instrument])
    quote_length = logic.longlong * 2 + 2
    pip_digit = logic.pip_digit

    start_time = time.time()
    logger.info(f"-------{instrument}----------")
    if instrument in list(position_units.keys()):
        end_time = time.time()
        duration = end_time - start_time
        start_time = time.time()
        logger.info(f"{instrument} has a position.")
        logger.info(f"execution time: {duration: .5f} sec")
        return

    qccm = QuoteCurrentCandleModel(
        granularity=granularity,
        instrument=instrument,
        price_type="M",
        stick_count=quote_length,
    )

    df = quote_client.quote_latest_candles(qccm)
    df_judgment = logic.generate_judgment_matrix(df)

    candle_time = df_judgment["time"].iloc[-1]
    buy_judgment = df_judgment["buy_judgment"].iloc[-1]
    sell_judgment = df_judgment["sell_judgment"].iloc[-1]
    current_price = df_judgment["close"].iloc[-1]

    # TODO: move pip round
    buy_stop_loss_price = round(
        df_judgment["buy_stop_loss_price"].iloc[-1], pip_digit + 1
    )
    buy_take_profit_price = round(
        df_judgment["buy_take_profit_price"].iloc[-1], pip_digit + 1
    )
    sell_stop_loss_price = round(
        df_judgment["sell_stop_loss_price"].iloc[-1], pip_digit + 1
    )
    sell_take_profit_price = round(
        df_judgment["sell_take_profit_price"].iloc[-1], pip_digit + 1
    )
    logger.info(
        f"{candle_time}, {buy_judgment}, {buy_stop_loss_price}, {buy_take_profit_price},{sell_judgment}, {sell_stop_loss_price}, {sell_take_profit_price}"
    )

    if buy_judgment:
        oom = OpenOrderModel(
            instrument=instrument,
            order_type="buy",
            current_price=current_price,
            stop_loss_price=buy_stop_loss_price,
            take_profit_price=buy_take_profit_price,
            units=units,
        )
        logger.info("buy order!!!")
    elif sell_judgment:
        oom = OpenOrderModel(
            instrument=instrument,
            order_type="sell",
            current_price=current_price,
            stop_loss_price=sell_stop_loss_price,
            take_profit_price=sell_take_profit_price,
            units=units,
        )
        logger.info("sell order!!!")
    else:
        end_time = time.time()
        duration = end_time - start_time
        start_time = time.time()
        logger.info(f"execution time: {duration: .5f} sec")
        return

    logger.info(f"{oom}")
    res = transaction_client.create_open_order_at_market(oom)
    logger.info(f"{res}")
