import pandas as pd
from app.indicators.moving_average import MovingAverage


class LongShortMACrossing:
    def __init__(self, long_term: int, short_term: int):
        self.long_term = long_term
        self.short_term = short_term

    def generate_judgment_matrix(self, candle_df):
        df = candle_df  # .iloc[-self.long_term - 1 :].copy()

        df["short"] = MovingAverage().sma(df["close"], self.short_term)
        df["long"] = MovingAverage().sma(df["close"], self.long_term)

        bull = df["short"] > df["long"]
        bull_prev = bull.shift(1)

        bear = df["short"] < df["long"]
        bear_prev = bear.shift(1)

        df["buy_judgment"] = bull & bear_prev
        df["sell_judgment"] = bull_prev & bear

        return df


def main():
    filename = "historical_data/sample_candles.csv"
    df = pd.read_csv(filename, nrows=30)

    logic = LongShortMACrossing(7, 3)
    df_judgment = logic.generate_judgment_matrix(df)

    print(df_judgment)


if __name__ == "__main__":
    main()
