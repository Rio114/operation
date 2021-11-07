import pandas as pd
from pandas.testing import assert_series_equal

from app.indicators.ichimoku import Ichimoku


class TestIchimoku:
    def setup(self):
        self.short = 2
        self.long = 4
        self.longlong = 8
        self.client = Ichimoku(short=self.short, long=self.long, longlong=self.longlong)
        cols = ["time", "open", "high", "low", "close"]
        dtypes = {"open": float, "high": float, "low": float, "close": float}
        values = [
            ["2021-05-02 21:00:00+00:00", 131.556, 131.571, 131.509, 131.556],
            ["2021-05-02 21:01:00+00:00", 131.509, 131.562, 131.490, 131.514],
            ["2021-05-02 21:02:00+00:00", 131.490, 131.547, 131.490, 131.514],
            ["2021-05-02 21:03:00+00:00", 131.546, 131.547, 131.507, 131.516],
            ["2021-05-02 21:05:00+00:00", 131.507, 131.536, 131.501, 131.501],
            ["2021-05-02 21:06:00+00:00", 131.538, 131.538, 131.502, 131.502],
            ["2021-05-02 21:08:00+00:00", 131.458, 131.506, 131.455, 131.455],
            ["2021-05-02 21:09:00+00:00", 131.504, 131.540, 131.455, 131.540],
            ["2021-05-02 21:10:00+00:00", 131.506, 131.541, 131.443, 131.452],
            ["2021-05-02 21:11:00+00:00", 131.499, 131.548, 131.442, 131.447],
            ["2021-05-02 21:12:00+00:00", 131.557, 131.560, 131.451, 131.451],
            ["2021-05-02 21:13:00+00:00", 131.503, 131.554, 131.453, 131.493],
            ["2021-05-02 21:14:00+00:00", 131.499, 131.502, 131.452, 131.452],
            ["2021-05-02 21:15:00+00:00", 131.503, 131.538, 131.453, 131.487],
            ["2021-05-02 21:16:00+00:00", 131.531, 131.542, 131.478, 131.478],
        ]

        self.df = pd.DataFrame(values, columns=cols).astype(dtypes)

    def test_generate_df(self):
        actual_df, cols = self.client.generate_df(self.df)
        actual = actual_df[cols].iloc[14]

        high_low = self.df[["high", "low"]].values

        basis = (high_low[-self.long :, 0].max() + high_low[-self.long :, 1].min()) / 2
        conversion = (
            high_low[-self.short :, 0].max() + high_low[-self.short :, 1].min()
        ) / 2

        _basis = self.client._generate_basis_line(self.df).shift(self.long).iloc[-1]
        _conversion = (
            self.client._generate_conversion_line(self.df).shift(self.long).iloc[-1]
        )
        span1 = (_basis + _conversion).values[0] / 2

        _max = high_low[-self.longlong - self.long :, 0].max()
        _min = high_low[-self.longlong - self.long :, 1].min()
        span2 = (_max + _min) / 2

        behind = None

        expected = (
            pd.DataFrame([[basis, conversion, span1, span2, behind]], columns=cols)
            .astype(float)
            .iloc[0]
        )
        expected.name = 14

        print(actual)
        print(expected)
        assert_series_equal(actual, expected)
