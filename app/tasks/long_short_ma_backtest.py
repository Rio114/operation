import pandas as pd
from app.logic.long_short_ma_crossing import LongShortMACrossing


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


def main():
    filename = "historical_data/USD_JPY_M15_M_20211106212354.csv"
    df_original = pd.read_csv(filename)

    cond_list = []
    for stop in range(20, 31, 1):
        for limit in range(20, 31, 1):
            for short in range(5, 10, 1):
                for long in range(short + 3, 21, 1):
                    cond_list.append((stop, limit, short, long))

    client = BackTest("USD_JPY")
    max_mean_profit = -10
    for cond in cond_list:
        logic = LongShortMACrossing(cond[2], cond[3])
        df = logic.generate_judgment_matrix(df_original)
        p, c = client.run_backtest(df, cond[0], cond[1], 0.8)
        if max_mean_profit < p / c:
            max_mean_profit = p / c
            best_cond = cond

            print(cond, max_mean_profit)

    print(best_cond, max_mean_profit)  # (28, 22, 8, 20) -0.0018265651438240911


if __name__ == "__main__":
    main()
