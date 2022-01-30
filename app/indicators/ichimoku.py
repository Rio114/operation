from typing import List, Tuple

import pandas as pd

from app.tasks import get_module_logger


class Ichimoku:
    def __init__(self, short, long, longlong):
        self.short = short
        self.long = long
        self.longlong = longlong
        self.price_cols = ["open", "high", "low", "close"]
        self.logger = get_module_logger(__name__)

    def generate_df(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        additional_df = pd.DataFrame(columns=df.columns, index=range(self.long))
        ichimoku_df = pd.concat([df, additional_df], axis=0).reset_index(drop=True)
        ichimoku_df["basis"] = self._generate_basis_line(ichimoku_df)
        ichimoku_df["conversion"] = self._generate_conversion_line(ichimoku_df)
        ichimoku_df["preceding_span1"] = self._generate_preceding_span_1_line(
            ichimoku_df
        )
        ichimoku_df["preceding_span2"] = self._generate_preceding_span_2_line(
            ichimoku_df
        )
        ichimoku_df["behind"] = self._generate_behind_line(ichimoku_df)
        added_cols = [
            "basis",
            "conversion",
            "preceding_span1",
            "preceding_span2",
            "behind",
        ]
        self.logger.debug("generated ichimoku_df")
        return ichimoku_df, added_cols

    def _generate_basis_line(self, df: pd.DataFrame) -> pd.Series:
        se_max = df["high"].rolling(self.long).max()
        se_min = df["low"].rolling(self.long).min()
        values = (se_max + se_min) / 2
        return values

    def _generate_conversion_line(self, df: pd.DataFrame) -> pd.Series:
        se_max = df["high"].rolling(self.short).max()
        se_min = df["low"].rolling(self.short).min()
        values = (se_max + se_min) / 2
        return values

    def _generate_preceding_span_1_line(self, df: pd.DataFrame) -> pd.DataFrame:
        basis = self._generate_basis_line(df)
        conversion = self._generate_conversion_line(df)
        values = (basis + conversion) / 2
        return values.shift(self.long)

    def _generate_preceding_span_2_line(self, df: pd.DataFrame) -> pd.DataFrame:
        high = df["high"]
        low = df["low"]
        se_max = high.rolling(self.longlong).max()
        se_min = low.rolling(self.longlong).min()
        values = (se_max + se_min) / 2
        return values.shift(self.long)

    def _generate_behind_line(self, df: pd.DataFrame) -> pd.DataFrame:
        behind = df["close"].shift(-self.long)
        behind.index = df.index
        return behind


def main():
    filename = "historical_data/sample_candles.csv"
    short = 2
    long = 4
    longlong = 8
    df = pd.read_csv(filename, nrows=longlong * 3)
    print(df)
    print("-" * 10)

    client = Ichimoku(short, long, longlong)
    ich_df, cols = client.generate_df(df)
    print(cols)
    print(ich_df.iloc[: longlong * 3 + 3])


if __name__ == "__main__":
    main()
