import pandas as pd
from app.indicators.ichimoku import Ichimoku
from app.logic.common import add_fixed_width_limit_prices


class IchimokuMethod:
    def __init__(
        self,
        short_term: int,
        long_term: int,
        longlong_term: int,
        stop_loss_pips: int,
        take_profit_pips: int,
        pip_basis: float,
    ):
        self.short_term = short_term
        self.long_term = long_term
        self.longlong_term = longlong_term
        self.stop_loss_pips = stop_loss_pips
        self.take_profit_pips = take_profit_pips
        self.pip_basis = pip_basis

    def generate_judgment_matrix(self, candle_df):
        client = Ichimoku(self.short_term, self.long_term, self.longlong_term)
        df, _ = client.generate_df(candle_df)

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

        df = add_fixed_width_limit_prices(
            df, self.stop_loss_pips, self.take_profit_pips, self.pip_basis
        )

        return df.iloc[: -self.long_term]


def main():
    filename = "historical_data/USD_JPY_M15_M_20211106212354.csv"
    df = pd.read_csv(filename, nrows=240)
    print(df.head())

    logic = IchimokuMethod(2, 4, 8, 10, 10, 0.01)
    df_judgment = logic.generate_judgment_matrix(df)
    cols_prices = [
        "high",
        "low",
        "close",
        "basis",
        "conversion",
        "preceding_span1",
        "preceding_span2",
        "behind",
        "buy_stop_loss",
        "buy_take_profit",
        "sell_stop_loss",
        "sell_take_profit",
    ]
    cols_judgment = [
        "b_judge_1",
        "b_judge_2",
        "b_judge_3",
        "buy_judgment",
        "s_judge_1",
        "s_judge_2",
        "s_judge_3",
        "sell_judgment",
    ]
    print(df_judgment[cols_prices].tail(30))
    print(df_judgment[cols_judgment].tail(30))


if __name__ == "__main__":
    main()
