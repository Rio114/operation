import datetime as dt
import time

import pandas as pd
from app.config import Config
from app.entities.candle import QuoteHistoricalCandleModel
from app.infra.candle.historical_candle import HistricalCandleFormatter
from oandapyV20.endpoints.instruments import (
    InstrumentsCandles as InstrumentsCandles_api,
)
from oandapyV20.exceptions import V20Error


class Candle:
    def __init__(self):
        config = Config()
        # self.account_id = config.ACCOUNT_ID
        self.api = config.api
        self.DATADIR = "historical_data/"
        self.Quotation_limit = 5000

    def quote_historical_candles(self, qhcm: QuoteHistoricalCandleModel):

        granularity = qhcm.granularity
        price_type = qhcm.price_type
        instrument = qhcm.instrument
        quote_from = qhcm.quote_from
        quote_to = qhcm.quote_to

        next_dt_str = (
            "-".join([quote_from[:4], quote_from[4:6], quote_from[6:]])
            + "T00:00:00+00:00"
        )
        next_dt = dt.datetime.strptime(next_dt_str, "%Y-%m-%dT%H:%M:%S+00:00")

        until_dt_str = (
            "-".join([quote_to[:4], quote_to[4:6], quote_to[6:]]) + "T00:00:00+00:00"
        )
        until_dt = dt.datetime.strptime(until_dt_str, "%Y-%m-%dT%H:%M:%S+00:00")

        params = {
            "from": next_dt_str,
            "count": self.Quotation_limit,
            "granularity": granularity,
            "price": price_type,
        }

        if granularity[0] == "S":
            time_increment = dt.timedelta(seconds=int(granularity[1:]))
        elif granularity[0] == "M":
            time_increment = dt.timedelta(minutes=int(granularity[1:]))
        elif granularity[0] == "H":
            time_increment = dt.timedelta(hours=int(granularity[1:]))
        elif granularity[0] == "D":
            time_increment = dt.timedelta(days=1)

        dfs = []
        while next_dt < until_dt:
            instruments_candles = InstrumentsCandles_api(
                instrument=instrument, params=params
            )

            try:
                self.api.request(instruments_candles)
                response = instruments_candles.response

            except V20Error as e:
                raise Exception(f"Error: {e}")

            if len(response["candles"]) == 0:
                break

            client = HistricalCandleFormatter()
            df_temp = client.assign_candles(response)

            next_dt = df_temp["time"].iloc[-1] + time_increment
            next_dt_str = next_dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
            next_dt = dt.datetime.strptime(next_dt_str, "%Y-%m-%dT%H:%M:%S+00:00")
            params["from"] = next_dt_str

            dfs.append(df_temp)
            time.sleep(1)

        df = pd.concat(dfs, axis=0).reset_index(drop=True)

        save_cols = [
            "time",
            "type",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "complete",
        ]

        df[save_cols].to_csv(
            self.DATADIR
            + f"{instrument}_{granularity}_{price_type}_{quote_from}_{quote_to}.csv",
            index=False,
        )
        return df[save_cols]


def main():
    qhcm = QuoteHistoricalCandleModel(
        granularity="S5",
        instrument="USD_JPY",
        price_type="M",
        quote_from="20211101",
        quote_to="20211104",
    )
    client = Candle()
    df = client.quote_historical_candles(qhcm)
    print(df)


if __name__ == "__main__":
    main()
