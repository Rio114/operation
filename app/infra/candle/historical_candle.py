from typing import Dict

import pandas as pd


class HistricalCandleFormatter:
    def __init__(self):
        self.output_dtypes = {
            "open": float,
            "high": float,
            "low": float,
            "close": float,
            "volume": int,
        }
        self.output_cols = [
            "time",
            "type",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "complete",
        ]

    def assign_candles(self, response_body: Dict) -> pd.DataFrame:

        df = pd.DataFrame(response_body["candles"])
        candle_types = df.columns[
            ~df.columns.isin(
                [
                    "volume",
                    "complete",
                    "time",
                ]
            )
        ]
        assert len(candle_types) == 1, "candle types in response must be unique"

        candle_type = candle_types.values[0]

        df["type"] = candle_type

        df["complete"] = df["complete"].apply(
            lambda x: True if x == "true" or x else False
        )
        df["time"] = pd.to_datetime(df["time"])

        df = self.__pickup_by_type(df, candle_type)

        return df[self.output_cols].astype(self.output_dtypes)

    def __pickup_by_type(self, df, candle_type: str) -> pd.DataFrame:

        df["open"] = df[candle_type].apply(lambda x: x["o"])
        df["high"] = df[candle_type].apply(lambda x: x["h"])
        df["low"] = df[candle_type].apply(lambda x: x["l"])
        df["close"] = df[candle_type].apply(lambda x: x["c"])

        return df
