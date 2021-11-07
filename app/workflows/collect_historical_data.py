def main():
    instruments = ["USD_JPY", "EUR_JPY", "EUR_USD"]
    for instrument in instruments:
        print(f"collecting {instrument} candles")
        print("formatting candles")
        print("load previous dataframe")
        print(f"concate previous and latest dataframe")


if __name__ == "__main__":
    main()
