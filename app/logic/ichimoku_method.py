import pandas as pd
from app.indicators.ichimoku import Ichimoku


class IchimokuMethod:
    def __init__(
        self,
        short_term: int,
        long_term: int,
        longlong_term: int,
    ):
        self.short_term = short_term
        self.long_term = long_term
        self.longlong_term = longlong_term

    def generate_judgment_matrix(self, candle_df):
        df_input = candle_df  # .iloc[-self.long_term - 1 :].copy()

        client = Ichimoku(self.short_term, self.long_term, self.longlong_term)
        df, _ = client.generate_df(df_input)

        # signal_1
        bull_1 = df["conversion"] > df["basis"]
        bear_1 = df["conversion"] < df["basis"]
        df["b_judge_1"] = bull_1
        df["s_judge_1"] = bear_1

        # signal_2
        bull_2 = (df["high"] < df["behind"]).shift(self.longlong_term)
        bear_2 = df["low"] > df["behind"].shift(self.longlong_term)
        df["b_judge_2"] = bull_2
        df["s_judge_2"] = bear_2

        # signal_3
        bull_3 = df["high"] > df[["preceding_span1", "preceding_span2"]].max(axis=1)
        bear_3 = df["low"] < df[["preceding_span1", "preceding_span2"]].min(axis=1)
        df["b_judge_3"] = bull_3
        df["s_judge_3"] = bear_3

        df["buy_judgment"] = df["b_judge_1"] & df["b_judge_2"] & df["b_judge_3"]
        df["sell_judgment"] = df["s_judge_1"] & df["s_judge_2"] & df["s_judge_3"]

        return df.copy()


def main():
    filename = "historical_data/USD_JPY_M15_M_20211106212354.csv"
    df = pd.read_csv(filename, nrows=240)

    logic = IchimokuMethod(2, 4, 8)
    df_judgment = logic.generate_judgment_matrix(df)
    cols = [
        "high",
        "low",
        "close",
        "basis",
        "conversion",
        "preceding_span1",
        "preceding_span2",
        "behind",
        "b_judge_1",
        "b_judge_2",
        "b_judge_3",
        "s_judge_1",
        "s_judge_2",
        "s_judge_3",
        "buy_judgment",
        "sell_judgment",
    ]

    print(df_judgment[cols].tail(30))


if __name__ == "__main__":
    main()
