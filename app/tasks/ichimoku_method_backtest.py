import pandas as pd
from app.logic.ichimoku_method import IchimokuMethod
from app.tasks.backtest import BackTest


def main():
    filename = "historical_data/USD_JPY_M15_M_20211106212354.csv"
    # filename = "historical_data/EUR_JPY_M15_M_20211106212412.csv"
    # filename = "historical_data/EUR_USD_M15_M_20211106212436.csv"
    df_original = pd.read_csv(filename)

    cond_list = []
    for stop in range(10, 51, 5):
        for limit in range(10, 51, 5):
            for short in range(7, 13, 1):
                for long in range(short * 2, short * 3, 2):
                    for longlong in range(short * 4, short * 5, 2):
                        cond_list.append((stop, limit, short, long, longlong))

    client = BackTest("USD_JPY")
    max_mean_profit = -10
    for cond in cond_list:

        logic = IchimokuMethod(cond[2], cond[3], cond[4])
        df = logic.generate_judgment_matrix(df_original)
        p, c = client.run_backtest(df, cond[0], cond[1], 0.8)
        if max_mean_profit < p / c:
            max_mean_profit = p / c
            best_cond = cond
            best_cond = cond
            best_profit = p
            best_cnt = c
            print(f"{best_cond}, {best_profit:.5f}, {best_cnt}, {max_mean_profit:5f}")

    print(f"{best_cond}, {best_profit:.5f}, {best_cnt}, {max_mean_profit:5f}")


if __name__ == "__main__":
    main()
