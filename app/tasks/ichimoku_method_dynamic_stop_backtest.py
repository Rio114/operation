from multiprocessing import Pool

import pandas as pd

from app.logic.ichimoku_method_dynamic_stop import IchimokuMethodDynamicStop
from app.tasks.backtest import BackTest


def main():
    # filename = "historical_data/USD_JPY_M15_M_20220122224030.csv"
    # filename = "historical_data/EUR_JPY_M15_M_20220122224102.csv"
    filename = "historical_data/EUR_USD_M15_M_20220122224117.csv"

    instrument = "EUR_USD"

    df_original = pd.read_csv(filename)

    cond_list = []

    for short in range(7, 13, 1):
        for long in range(short * 2, short * 3, 2):
            for longlong in range(short * 4, short * 5, 2):
                cond_list.append(
                    [
                        df_original,
                        instrument,
                        short,
                        long,
                        longlong,
                    ]
                )

    print("start multiprocess")
    pool = Pool(8)
    result = pool.map(backtest_process, cond_list)
    pool.close()
    print("finish multiprocess")
    result_df = (
        pd.DataFrame(
            result,
            columns=[
                "instrument",
                "short",
                "long",
                "longlong",
                "profit",
                "count",
                "win_count",
                "loose_count",
            ],
        )
        .sort_values("profit", ascending=False)
        .reset_index(drop=True)
    )
    print(result_df.head(20))
    print(result_df.tail(5))

    best_record = result_df.iloc[0].values
    best_cond = best_record[1:4]
    best_profit = best_record[4]
    best_count = best_record[5]
    best_mean_profit = best_profit / best_count
    print(f"{best_cond}, {best_profit:.5f}, {best_count}, {best_mean_profit:5f}")

    best_input = [df_original, instrument]
    best_input.extend(best_cond)
    _, _, _, _, best_df = gen_backtest_df(best_input)

    short = best_cond[0]
    long = best_cond[1]
    longlong = best_cond[2]

    best_df.to_csv(
        f"backtest_ichimoku_dynamic_stop_{instrument}_{short}_{long}_{longlong}.csv",
        index=False,
    )
    print(best_df)


def backtest_process(inputs):
    _, instrument, short, long, longlong = inputs
    p, c, wc, lc, df = gen_backtest_df(inputs)
    return [instrument, short, long, longlong, p, c, wc, lc]


def gen_backtest_df(inputs):
    df_original, instrument, short, long, longlong = inputs
    if instrument == "EUR_USD":
        pip_basis = 0.0001
    else:
        pip_basis = 0.01
    client = BackTest(instrument, 0.8)
    logic = IchimokuMethodDynamicStop(
        short,
        long,
        longlong,
        pip_basis,
    )
    df = logic.generate_judgment_matrix(df_original)
    p, c, wc, lc, df = client.run_backtest(df)
    return p, c, wc, lc, df


if __name__ == "__main__":
    main()
