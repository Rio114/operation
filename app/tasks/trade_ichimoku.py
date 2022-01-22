import time

import yaml
from app.config import Config
from app.entities.candle import QuoteCurrentCandleModel
from app.entities.transaction import OpenOrderModel
from app.infra.api.candle import Candle
from app.infra.api.transaction import Transaction
from app.logic.ichimoku_method import IchimokuMethod
from app.tasks import get_module_logger


def trade():
    logger = get_module_logger(__name__)

    config = Config()
    # instruments = ["USD_JPY", "EUR_JPY", "EUR_USD"]
    instruments = ["USD_JPY"]
    granularity = "M15"
    units = config.UNITS

    with open("app/ichimoku_params.yaml", "r") as yml:
        ichimoku_params = yaml.safe_load(yml)

    transaction_client = Transaction()
    positions = transaction_client.find_current_positions()

    logger.info("------current positions------")

    position_units = {}
    for position in positions:
        position_units[position.instrument] = position.units

    logger.info(position_units)
    quote_client = Candle()

    start_time = time.time()
    for instrument in instruments:
        logger.info(f"-------{instrument}----------")
        if instrument in list(position_units.keys()):
            end_time = time.time()
            duration = end_time - start_time
            start_time = time.time()
            logger.info(f"{instrument} has a position.")
            logger.info(f"execution time: {duration: .5f} sec")
            continue

        if instrument == "EUR_USD":
            pip_digit = 4
            pip_basis = 0.1 ** pip_digit
        else:
            pip_digit = 2
            pip_basis = 0.1 ** pip_digit

        params = ichimoku_params[instrument]
        short = params["ICHIMOKU"][0]
        long = params["ICHIMOKU"][1]
        longlong = params["ICHIMOKU"][2]
        stop_loss_pips = params["STOP"]
        take_profit_pips = params["PROFIT"]

        qccm = QuoteCurrentCandleModel(
            granularity=granularity,
            instrument=instrument,
            price_type="M",
            stick_count=longlong * 2 + 2,
        )

        df = quote_client.quote_latest_candles(qccm)
        logic = IchimokuMethod(
            short, long, longlong, stop_loss_pips, take_profit_pips, pip_basis
        )
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
            continue

        logger.info(f"{oom}")
        res = transaction_client.create_open_order_at_market(oom)
        logger.info(f"{res}")


if __name__ == "__main__":
    trade()
