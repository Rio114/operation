import argparse
import datetime as dt
import time

import pandas as pd
from oandapyV20.endpoints.instruments import InstrumentsCandles
from oandapyV20.exceptions import V20Error

from app.config import Config
from app.infra.candle.historical_candle import HistricalCandleFormatter

"""
poetry run python -m app.tasks.get_historical_candles -g M15 -i USD_JPY -p M
"""


def main():
    config = Config()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-g",
        "--granularity",
        type=str,
        choices=["S5", "M1", "M15", "H1", "D"],  # time diff must be changed
        required=True,
    )
    parser.add_argument(
        "-i",
        "--instrument",
        type=str,
        choices=["USD_JPY", "EUR_USD", "EUR_JPY"],
        required=True,
    )
    parser.add_argument(
        "-p", "--price_type", type=str, choices=["M", "A", "B"], required=True
    )

    args = parser.parse_args()
    granularity = args.granularity
    price_type = args.price_type
    instrument = args.instrument
    download_dt = dt.datetime.now().strftime("%Y%m%d%H%M%S")

    save_cols = ["time", "type", "open", "high", "low", "close", "volume", "complete"]
    name_cols = ["instrument", "granularity", "type"]

    next_dt_str = "2021-05-01T00:00:00+00:00"
    next_dt = dt.datetime.strptime(next_dt_str, "%Y-%m-%dT%H:%M:%S+00:00")

    until_dt_str = "2022-01-21T00:00:00+00:00"
    until_dt = dt.datetime.strptime(until_dt_str, "%Y-%m-%dT%H:%M:%S+00:00")

    params = {
        "from": next_dt_str,
        "count": 5000,
        "granularity": granularity,
        "price": price_type,
    }

    dfs = []
    while next_dt < until_dt:
        print(next_dt_str)
        instruments_candles = InstrumentsCandles(instrument=instrument, params=params)
        try:
            config.api.request(instruments_candles)
            response = instruments_candles.response

        except V20Error as e:
            raise Exception(f"Error: {e}")

        client = HistricalCandleFormatter()

        if len(response["candles"]) == 0:
            break

        df_temp = client.assign_candles(response)
        next_dt = df_temp["time"].iloc[-1] + dt.timedelta(minutes=1)
        next_dt_str = next_dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        next_dt = dt.datetime.strptime(next_dt_str, "%Y-%m-%dT%H:%M:%S+00:00")
        params["from"] = next_dt_str

        dfs.append(df_temp)
        time.sleep(1)

    df = pd.concat(dfs, axis=0).reset_index(drop=True)
    print(df.head())
    print("-" * 10)
    print(df.tail())

    df[save_cols].to_csv(
        f"{instrument}_{granularity}_{price_type}_{download_dt}.csv", index=False
    )


if __name__ == ("__main__"):
    main()
