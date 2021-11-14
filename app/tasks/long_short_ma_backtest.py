import pandas as pd
from app.logic.long_short_ma_crossing import LongShortMACrossing
from app.tasks.backtest import BackTest


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
            best_profit = p
            best_cnt = c
            print(best_cond, best_profit, best_cnt, max_mean_profit)

    print(best_cond, best_profit, best_cnt, max_mean_profit)


if __name__ == "__main__":
    main()
