import pandas as pd
from app.indicators.ichimoku import Ichimoku
from app.logic.common import add_fixed_width_limit_prices


class IchimokuMethod:
    def __init__(
        self,
        params,
    ):
        self.short = params["ICHIMOKU"][0]
        self.long = params["ICHIMOKU"][1]
        self.longlong = params["ICHIMOKU"][2]
        self.stop_loss_pips = params["STOP"]
        self.take_profit_pips = params["PROFIT"]

        self.pip_digit = params["PIP_DIGIT"]
        self.pip_basis = 0.1 ** self.pip_digit

    def generate_judgment_matrix(self, candle_df):
        client = Ichimoku(self.short_term, self.long_term, self.longlong_term)
        df, _ = client.generate_df(candle_df)

        # signal_1
        df["buy_1"] = df["conversion"] > df["basis"]
        df["sell_1"] = df["conversion"] < df["basis"]

        # signal_2
        df["buy_2"] = (df["high"] < df["behind"]).shift(self.long_term)
        df["sell_2"] = (df["low"] > df["behind"]).shift(self.long_term)

        # signal_3
        df["buy_3"] = df["high"] > df[["preceding_span1", "preceding_span2"]].max(
            axis=1
        )
        df["sell_3"] = df["low"] < df[["preceding_span1", "preceding_span2"]].min(
            axis=1
        )

        # df["buy_judgment"] = df["buy_1"] & df["buy_2"] & df["buy_3"]
        # df["sell_judgment"] = df["sell_1"] & df["sell_2"] & df["sell_3"]

        df["current_buy_judgment"] = (df["buy_1"] & df["buy_2"] & df["buy_3"]).astype(
            bool
        )
        df["previous_buy_judgment"] = df["current_buy_judgment"].shift(1)
        df["current_sell_judgment"] = (
            df["sell_1"] & df["sell_2"] & df["sell_3"]
        ).astype(bool)
        df["previous_sell_judgment"] = df["current_sell_judgment"].shift(1)

        df["buy_judgment"] = ~(df["previous_buy_judgment"].astype(bool)) & df[
            "current_buy_judgment"
        ].astype(bool)
        df["sell_judgment"] = ~(df["previous_sell_judgment"]).astype(bool) & df[
            "current_sell_judgment"
        ].astype(bool)

        df = add_fixed_width_limit_prices(
            df, self.stop_loss_pips, self.take_profit_pips, self.pip_basis
        )

        return df.iloc[: -self.long_term]


def main():
    filename = "historical_data/USD_JPY_M15_M_20211201_20211210.csv"
    df = pd.read_csv(filename)
    print(df.head())

    logic = IchimokuMethod(12, 26, 56, 30, 55, 0.01)
    df_judgment = logic.generate_judgment_matrix(df.iloc[:768])
    cols_prices = [
        "high",
        "low",
        "close",
        "basis",
        "conversion",
        "preceding_span1",
        "preceding_span2",
        "behind",
        "buy_stop_loss_price",
        "buy_take_profit_price",
        "sell_stop_loss_price",
        "sell_take_profit_price",
    ]
    cols_judgment = [
        "buy_1",
        "buy_2",
        "buy_3",
        "buy_judgment",
        "sell_1",
        "sell_2",
        "sell_3",
        "sell_judgment",
    ]
    print(df_judgment)
    print(df_judgment[cols_prices].tail(30))
    print(df_judgment[cols_judgment].tail(30))
    df_judgment.to_csv("test.csv")


if __name__ == "__main__":
    main()
