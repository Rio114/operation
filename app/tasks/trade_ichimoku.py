import time

import yaml

from app.config import Config
from app.entities.candle import QuoteCurrentCandleModel
from app.entities.transaction import OpenOrderModel
from app.infra.api.candle import Candle
from app.infra.api.transaction import Transaction
from app.logic.ichimoku_method import IchimokuMethod


def main():
    config = Config()
    instruments = ["USD_JPY", "EUR_JPY", "EUR_USD"]
    granularity = "M15"
    units = config.UNITS

    with open("app/ichimoku_params.yaml", "r") as yml:
        ichimoku_params = yaml.safe_load(yml)

    transaction_client = Transaction()
    positions = transaction_client.find_current_positions()
    print("------current positions------")

    position_units = {}
    for position in positions:
        position_units[position.instrument] = position.units
    print(position_units)

    quote_client = Candle()

    start_time = time.time()
    for instrument in instruments:
        print(f"-------{instrument}----------")
        if instrument in list(position_units.keys()):
            end_time = time.time()
            duration = end_time - start_time
            start_time = time.time()
            print(f"{instrument} has a position.")
            print(f"execution time: {duration: .5f} sec")
            continue

        params = ichimoku_params[instrument]
        stop_loss_pips = params["STOP"]
        take_profit_pips = params["PROFIT"]
        short = params["ICHIMOKU"][0]
        long = params["ICHIMOKU"][1]
        longlong = params["ICHIMOKU"][2]

        qccm = QuoteCurrentCandleModel(
            granularity=granularity,
            instrument=instrument,
            price_type="M",
            stick_count=longlong,
        )

        if instrument == "EUR_USD":
            pip_basis = 0.0001
        else:
            pip_basis = 0.01

        df = quote_client.quote_latest_candles(qccm)
        logic = IchimokuMethod(
            short, long, longlong, stop_loss_pips, take_profit_pips, pip_basis
        )
        df_judgment = logic.generate_judgment_matrix(df)

        candle_time = df_judgment["time"].iloc[-1]
        buy_judgment = df_judgment["buy_judgment"].iloc[-1]
        sell_judgment = df_judgment["sell_judgment"].iloc[-1]
        print(candle_time, buy_judgment, sell_judgment)

        if buy_judgment:
            oom = OpenOrderModel(
                instrument=instrument,
                order_type="buy",
                current_price=df_judgment["close"].iloc[-1],
                stop_loss_price=df_judgment["buy_stop_loss_price"].iloc[-1],
                take_profit_price=df_judgment["buy_take_profit_price"].iloc[-1],
                units=units,
            )
            print("buy order!!!")
        elif sell_judgment:
            oom = OpenOrderModel(
                instrument=instrument,
                order_type="sell",
                current_price=df_judgment["close"].iloc[-1],
                stop_loss_price=df_judgment["sell_stop_loss_price"].iloc[-1],
                take_profit_price=df_judgment["sell_take_profit_price"].iloc[-1],
                units=units,
            )
            print("sell order!!!")
        else:
            end_time = time.time()
            duration = end_time - start_time
            start_time = time.time()
            print(f"execution time: {duration: .5f} sec")
            continue

        print("send order")
        res = transaction_client.create_open_order_at_market(oom)
        print(res)

        # order(instrument, judgment, units)


if __name__ == "__main__":
    main()
