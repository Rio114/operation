import pandas as pd
from pandas.testing import assert_series_equal

from app.indicators.moving_average import MovingAverage


class TestHistoricalDataFormatter:
    def test_sma(self):
        indicator = MovingAverage()

        se = pd.Series(
            [x for x in range(20)],
            index=pd.date_range(start="2021-01-01", end="2021-01-20", freq="D"),
        )

        actual = indicator.sma(se, 5)

        expected_values = [None] * 4
        expected_values.extend([float(x) for x in range(2, 18, 1)])

        expected = pd.Series(
            expected_values,
            index=pd.date_range(start="2021-01-01", end="2021-01-20", freq="D"),
        )

        assert_series_equal(actual, expected)
