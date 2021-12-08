from typing import List

from app.config import Config
from app.entities.transaction import CloseOrderModel, OpenOrderModel, PositionModel
from oandapyV20.endpoints import orders as orders_api
from oandapyV20.endpoints import positions as positions_api


class Transaction:
    def __init__(self):
        config = Config()
        self.account_id = config.ACCOUNT_ID
        self.api = config.api

    def find_current_positions(self) -> List[PositionModel]:
        res = positions_api.OpenPositions(accountID=self.account_id)
        _ = self.api.request(res)
        responded_positions = res.response["positions"]

        if len(responded_positions) == 0:
            return []

        current_positions = []
        for position in responded_positions:
            if int(position["long"]["units"]) > 0:
                position_type = "long"
            else:
                position_type = "short"

            position_model = PositionModel(
                id=int(position[position_type]["tradeIDs"][0]),
                trade_ids=[int(i) for i in position[position_type]["tradeIDs"]],
                instrument=position["instrument"],
                position_type=position_type,
                average_price=float(position[position_type]["averagePrice"]),
                units=int(position[position_type]["units"]),
                unrealized_profit_loss=float(position[position_type]["unrealizedPL"]),
            )
            current_positions.append(position_model)

        return current_positions

    def find_close_orders(self) -> List[CloseOrderModel]:
        res = orders_api.OrderList(accountID=self.account_id)
        _ = self.api.request(res)
        responded_orders = res.response["orders"]
        if len(responded_orders) == 0:
            return []

        current_orders = []
        for order in responded_orders:
            order_model = CloseOrderModel(
                id=order["id"],
                position_id=order["tradeID"],
                order_type=order["type"],
                price=float(order["price"]),
            )
            current_orders.append(order_model)

        return current_orders

    def create_open_order_at_market(self, oom: OpenOrderModel) -> str:
        instrument = oom.instrument

        if instrument == "EUR_USD":
            pip_digit = 4
        else:
            pip_digit = 2

        if oom.order_type == "buy":
            order_type_flg = 1
        elif oom.order_type == "sell":
            order_type_flg = -1

        units = order_type_flg * oom.units
        stop_loss_price = round(
            oom.stop_loss_price,
            pip_digit + 1,
        )
        take_profit_price = round(
            oom.take_profit_price,
            pip_digit + 1,
        )

        data = {
            "order": {
                "stopLossOnFill": {"timeInForce": "GTC", "price": f"{stop_loss_price}"},
                "takeProfitOnFill": {"price": f"{take_profit_price}"},
                "timeInForce": "FOK",
                "instrument": f"{instrument}",
                "units": f"{units}",
                "type": "MARKET",
                "positionFill": "DEFAULT",
            }
        }

        res = orders_api.OrderCreate(accountID=self.account_id, data=data)
        _ = self.api.request(res)
        return res.response

    def close_current_position(self, instrument: str, position_type: str):
        if position_type == "buy":
            data = {"longUnits": "ALL"}
        elif position_type == "sell":
            data = {"shortUnits": "ALL"}
        else:
            return []

        res = positions_api.PositionClose(
            accountID=self.account_id, instrument=instrument, data=data
        )
        _ = self.api.request(res)
        return res.response


def main():
    transaction = Transaction()
    positions = transaction.find_current_positions()
    print("------current positions------")
    print(positions)

    orders = transaction.find_close_orders()
    print("------current orders------")
    print(orders)

    current_price = 1.12639
    stop_loss_price = 1.12839
    take_profit_price = 1.12439
    units = 11

    open_order = OpenOrderModel(
        instrument="EUR_USD",
        order_type="sell",
        current_price=current_price,
        stop_loss_price=stop_loss_price,
        take_profit_price=take_profit_price,
        units=units,
    )
    print("------send orders------")
    print(open_order)
    res = transaction.create_open_order_at_market(open_order)
    print(res)

    print("------close position orders------")
    # res = transaction.close_current_position("USD_JPY", "long")
    # print(res)

    print("-------end of process-------")


if __name__ == "__main__":
    main()
