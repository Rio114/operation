import pandas as pd
from app.logic.long_short_ma_crossing import LongShortMACrossing


def main():
    filename = "historical_data/sample_candles.csv"

    limit = 0.1
    stop = 0.1

    df = pd.read_csv(filename, nrows=30)

    logic = LongShortMACrossing(7, 3)
    df = logic.generate_judgment_matrix(df)

    df["buy_price"] = df["close"].where(df["buy_judgment"], None)
    df["buy_stop"] = (df["close"] - stop).where(df["buy_judgment"], None)
    df["buy_limit"] = (df["close"] + limit).where(df["buy_judgment"], None)

    df["sell_price"] = df["close"].where(df["sell_judgment"], None)
    df["sell_stop"] = (df["close"] + stop).where(df["sell_judgment"], None)
    df["sell_limit"] = (df["close"] - limit).where(df["sell_judgment"], None)

    cols = ["time", "open", "high", "low", "close", "buy_price", "buy_stop", "buy_limit"]
    print(df[cols])


if __name__ == "__main__":
    main()
