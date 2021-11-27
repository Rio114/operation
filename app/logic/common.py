import pandas as pd


def add_fixed_width_limit_prices(
    candle_df: pd.DataFrame,
    stop_loss_pips: int,
    take_profit_pips: int,
    pip_basis: float,
):
    stop_loss_width = stop_loss_pips * pip_basis
    take_profit_width = take_profit_pips * pip_basis

    candle_df["buy_stop_loss"] = candle_df["close"] - stop_loss_width
    candle_df["buy_take_profit"] = candle_df["close"] + take_profit_width

    candle_df["sell_stop_loss"] = candle_df["close"] + stop_loss_width
    candle_df["sell_take_profit"] = candle_df["close"] - take_profit_width

    return candle_df
