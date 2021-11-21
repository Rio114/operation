from multiprocessing import Pool

import pandas as pd
from app.logic.ichimoku_method import IchimokuMethod
from app.tasks.backtest import BackTest


def main():
    filename = "historical_data/USD_JPY_M15_M_20211106212354.csv"
    # filename = "historical_data/EUR_JPY_M15_M_20211106212412.csv"
    # filename = "historical_data/EUR_USD_M15_M_20211106212436.csv"

    instrument = "USD_JPY"

    df_original = pd.read_csv(filename)

    cond_list = []
    for stop in range(20, 51, 5):
        for limit in range(20, 101, 5):
            for short in range(7, 13, 1):
                for long in range(short * 2, short * 3, 2):
                    for longlong in range(short * 4, short * 5, 2):
                        cond_list.append(
                            [
                                df_original,
                                instrument,
                                stop,
                                limit,
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
                "stop",
                "limit",
                "short",
                "long",
                "longlong",
                "profit",
                "count",
            ],
        )
        .sort_values("profit", ascending=False)
        .reset_index(drop=True)
    )
    print(result_df.head(20))

    best_record = result_df.iloc[0].values
    best_cond = best_record[1:6]
    best_profit = best_record[6]
    best_count = best_record[7]
    best_mean_profit = best_profit / best_count
    print(f"{best_cond}, {best_profit:.5f}, {best_count}, {best_mean_profit:5f}")

    best_input = [df_original, instrument]
    best_input.extend(best_cond)
    _, _, best_df = gen_backtest_df(best_input)

    stop = best_cond[0]
    limit = best_cond[1]
    short = best_cond[2]
    long = best_cond[3]
    longlong = best_cond[4]

    best_df.to_csv(
        f"backtest_ichimoku_{instrument}_{stop}_{limit}_{short}_{long}_{longlong}.csv",
        index=False,
    )
    print(best_df)


def backtest_process(inputs):
    _, instrument, stop, limit, short, long, longlong = inputs
    p, c, df = gen_backtest_df(inputs)
    return [instrument, stop, limit, short, long, longlong, p, c]


def gen_backtest_df(inputs):
    df_original, instrument, stop, limit, short, long, longlong = inputs
    client = BackTest(instrument)
    logic = IchimokuMethod(short, long, longlong)
    df = logic.generate_judgment_matrix(df_original)
    p, c, df = client.run_backtest(df, stop, limit, 0.8)
    return p, c, df


if __name__ == "__main__":
    main()
