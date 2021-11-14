import pandas as pd


class BackTest:
    def __init__(self, instrument: str):
        is_JPY = instrument[-3:] == "JPY"

        if is_JPY:
            self.pip_basis = 0.01
        else:
            self.pip_basis = 0.0001

    def run_backtest(
        self, df: pd.DataFrame, stop_pips: int, limit_pips: int, split_pips: float
    ):
        """
        TODO: logger
        """
        stop = stop_pips * self.pip_basis
        limit = limit_pips * self.pip_basis
        split = split_pips * self.pip_basis

        position = 0
        profit = 0
        cnt = 0

        for row in df.itertuples():

            if row.buy_judgment & (position == 0):
                position = row.close
                continue
            elif row.sell_judgment & (position == 0):
                position = -row.close
                continue

            if position != 0:
                if position > 0:
                    high_price = row.high
                    low_price = row.low
                    close_price = row.close
                elif position < 0:
                    high_price = -row.low
                    low_price = -row.high
                    close_price = -row.close

                if low_price < position - stop:
                    diff_profit = -stop - split
                    profit += diff_profit
                    cnt += 1
                    position = 0
                    continue
                elif high_price > position + limit:
                    diff_profit = limit - split
                    profit += diff_profit
                    position = 0
                    cnt += 1
                    continue
                elif (position > 0) & (row.sell_judgment):
                    diff_profit = close_price - position - split
                    profit += diff_profit
                    cnt += 1
                    position = -close_price
                    continue
                elif (position < 0) & (row.buy_judgment):
                    diff_profit = close_price - position - split
                    profit += diff_profit
                    cnt += 1
                    position = -close_price
                    continue

        return profit, cnt
