import pandas as pd


class BackTest:
    def __init__(self, instrument: str):
        is_JPY = instrument[-3:] == "JPY"

        if is_JPY:
            self.pip_basis = 0.01
        else:
            self.pip_basis = 0.0001

    def run_backtest(
        self,
        df: pd.DataFrame,
        stop_pips: int,
        limit_pips: int,
        split_pips: float,
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
        open_idx = -1
        close_idx = -1
        records = []

        for row in df.itertuples():
            idx = row.time

            if row.buy_judgment & (position == 0):
                position = row.close
                open_idx = idx
                position_type = "buy"
                continue
            elif row.sell_judgment & (position == 0):
                position = -row.close
                open_idx = idx
                position_type = "sell"
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
                    close_position = position - stop
                    diff_profit = -stop - split
                    profit += diff_profit
                    close_idx = idx
                    records.append(
                        [
                            open_idx,
                            close_idx,
                            position_type,
                            position,
                            close_position,
                            diff_profit,
                            profit,
                        ]
                    )
                    position = 0
                    cnt += 1
                    continue
                elif high_price > position + limit:
                    close_position = position + limit
                    diff_profit = limit - split
                    profit += diff_profit
                    records.append(
                        [
                            open_idx,
                            close_idx,
                            position_type,
                            position,
                            close_position,
                            diff_profit,
                            profit,
                        ]
                    )
                    position = 0
                    cnt += 1
                    close_idx = idx
                    continue

            # if position != 0 & reverse:
            #     if (position > 0) & (row.sell_judgment):
            #         close_position = close_price
            #         diff_profit = close_price - position - split
            #         profit += diff_profit
            #         close_idx = idx
            #         records.append(
            #             [
            #                 open_idx,
            #                 close_idx,
            #                 position_type,
            #                 position,
            #                 close_position,
            #                 diff_profit,
            #                 profit,
            #             ]
            #         )
            #         position_type = "sell"
            #         cnt += 1
            #         position = -close_price
            #         open_idx = idx
            #         continue
            #     elif (position < 0) & (row.buy_judgment):
            #         close_position = close_price
            #         diff_profit = close_price - position - split
            #         profit += diff_profit
            #         close_idx = idx
            #         records.append(
            #             [
            #                 open_idx,
            #                 close_idx,
            #                 position_type,
            #                 position,
            #                 close_position,
            #                 diff_profit,
            #                 profit,
            #             ]
            #         )
            #         position_type = "buy"
            #         cnt += 1
            #         position = -close_price
            #         open_idx = idx
            #         continue

        record_df = pd.DataFrame(
            records,
            columns=[
                "open_idx",
                "close_idx",
                "position_type",
                "open_price",
                "close_price",
                "transaction_profit",
                "cum_profit",
            ],
        )
        return profit, cnt, record_df
