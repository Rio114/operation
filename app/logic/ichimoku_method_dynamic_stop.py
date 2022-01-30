import pandas as pd
from app.indicators.ichimoku import Ichimoku


class IchimokuMethodDynamicStop:
    def __init__(
        self,
        params,
    ):
        self.short = params["ICHIMOKU"][0]
        self.long = params["ICHIMOKU"][1]
        self.longlong = params["ICHIMOKU"][2]
        # stop_loss_pips = params["STOP"]
        # take_profit_pips = params["PROFIT"]

        self.pip_digit = params["PIP_DIGIT"]
        self.pip_basis = 0.1 ** self.pip_digit

    def generate_judgment_matrix(self, candle_df):
        client = Ichimoku(self.short, self.long, self.longlong)
        df, _ = client.generate_df(candle_df)

        # signal_1
        df["buy_1"] = df["conversion"] > df["basis"]
        df["sell_1"] = df["conversion"] < df["basis"]

        # signal_2
        df["buy_2"] = (df["high"] < df["behind"]).shift(self.long)
        df["sell_2"] = (df["low"] > df["behind"]).shift(self.long)

        # signal_3
        df["buy_3"] = df["high"] > df[["preceding_span1", "preceding_span2"]].max(
            axis=1
        )
        df["sell_3"] = df["low"] < df[["preceding_span1", "preceding_span2"]].min(
            axis=1
        )

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

        df["buy_stop_loss_price"] = df["low"].rolling(self.longlong).min()
        df["buy_take_profit_price"] = (
            df["close"] + df["close"] - df["buy_stop_loss_price"]
        )

        df["sell_stop_loss_price"] = df["high"].rolling(self.longlong).max()
        df["sell_take_profit_price"] = (
            df["close"] - df["sell_stop_loss_price"] + df["close"]
        )
        return df.iloc[: -self.long]


def main():
    filename = "historical_data/USD_JPY_M15_M_20211201_20211210.csv"
    df = pd.read_csv(filename)
    print(df.head())

    logic = IchimokuMethodDynamicStop(12, 26, 56, 0.01)
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
        "previous_buy_judgment",
        "current_buy_judgment",
        "buy_judgment",
        "sell_1",
        "sell_2",
        "sell_3",
        "previous_sell_judgment",
        "current_sell_judgment",
        "sell_judgment",
    ]
    print(df_judgment)
    print(df_judgment[cols_prices].tail(50))
    print(df_judgment[cols_judgment].tail(50))
    df_judgment.to_csv("test.csv")


if __name__ == "__main__":
    main()
