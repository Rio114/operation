import pandas as pd
from app.logic.common import add_fixed_width_limit_prices


class BackTest:
    def __init__(self, instrument: str, split_pips: float):
        is_JPY = instrument[-3:] == "JPY"

        if is_JPY:
            self.pip_basis = 0.01
        else:
            self.pip_basis = 0.0001

        self.default_stop_loss_pips = 20
        self.default_take_profit_pips = 20
        self.split = split_pips * self.pip_basis

    def run_backtest(
        self,
        df: pd.DataFrame,
    ):

        if "buy_stop_loss_price" not in list(df.columns):
            df = add_fixed_width_limit_prices(
                df,
                self.default_stop_loss_pips,
                self.default_take_profit_pips,
                self.pip_basis,
            )

        position = 0
        profit = 0
        cnt = 0
        win_cnt = 0
        loose_cnt = 0
        open_idx = -1
        close_idx = -1
        records = []

        for row in df.itertuples():
            idx = row.time

            if row.buy_judgment & (position == 0):
                position = row.close
                open_idx = idx
                position_type = "buy"
                stop_loss_price = row.buy_stop_loss_price
                take_profit_price = row.buy_take_profit_price
                continue
            elif row.sell_judgment & (position == 0):
                position = -row.close
                open_idx = idx
                position_type = "sell"
                stop_loss_price = -row.sell_stop_loss_price
                take_profit_price = -row.sell_take_profit_price
                continue

            if position != 0:
                if position > 0:
                    high_price = row.high
                    low_price = row.low
                elif position < 0:
                    high_price = -row.low
                    low_price = -row.high

                if low_price < stop_loss_price:
                    close_position = stop_loss_price
                    diff_profit = close_position - position - self.split
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
                    loose_cnt += 1
                    continue
                elif high_price > take_profit_price:
                    close_position = take_profit_price
                    diff_profit = close_position - position - self.split
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
                    win_cnt += 1
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
        return profit, cnt, win_cnt, loose_cnt, record_df
