import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from app.infra.candle.historical_candle import HistricalCandleFormatter


class TestHistoricalResponseFormatter:
    def test_assign_bid_candle(self):
        client = HistricalCandleFormatter()

        response_body = {
            "instrument": "USD_JPY",
            "granularity": "D",
            "candles": [
                {
                    "complete": "true",
                    "volume": 53353,
                    "time": "2021-09-07T21:00:00.000000000Z",
                    "bid": {
                        "o": "110.229",
                        "h": "110.442",
                        "l": "110.135",
                        "c": "110.258",
                    },
                },
                {
                    "complete": "true",
                    "volume": 58930,
                    "time": "2021-09-08T21:00:00.000000000Z",
                    "bid": {
                        "o": "110.205",
                        "h": "110.267",
                        "l": "109.615",
                        "c": "109.727",
                    },
                },
            ],
        }

        actual = client.assign_candles(response_body)

        expected_cols = [
            "time",
            "type",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "complete",
        ]

        expected_values = [
            [
                "2021-09-07T21:00:00.000000000Z",
                "bid",
                110.229,
                110.442,
                110.135,
                110.258,
                53353,
                True,
            ],
            [
                "2021-09-08T21:00:00.000000000Z",
                "bid",
                110.205,
                110.267,
                109.615,
                109.727,
                58930,
                True,
            ],
        ]

        expected_dtypes = {
            "open": float,
            "high": float,
            "low": float,
            "close": float,
            "volume": int,
        }
        expected = pd.DataFrame(expected_values, columns=expected_cols).astype(
            expected_dtypes
        )
        expected["time"] = pd.to_datetime(expected["time"])

        assert_frame_equal(actual, expected)

    def test_assign_bidask_candle(self):
        client = HistricalCandleFormatter()

        response_body = {
            "instrument": "USD_JPY",
            "granularity": "D",
            "candles": [
                {
                    "complete": "true",
                    "volume": 53353,
                    "time": "2021-09-07T21:00:00.000000000Z",
                    "bid": {
                        "o": "110.229",
                        "h": "110.442",
                        "l": "110.135",
                        "c": "110.258",
                    },
                },
                {
                    "complete": "true",
                    "volume": 58930,
                    "time": "2021-09-08T21:00:00.000000000Z",
                    "ask": {
                        "o": "110.205",
                        "h": "110.267",
                        "l": "109.615",
                        "c": "109.727",
                    },
                },
            ],
        }

        with pytest.raises(Exception) as e:
            _ = client.assign_candles(response_body)

        assert str(e.value) == "candle types in response must be unique"
