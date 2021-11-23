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

    def create_open_order_at_market(self, open_order: OpenOrderModel) -> str:
        pip_digit = 2
        pip_basis = 10 ** (-pip_digit)
        instrument = open_order.instrument

        if open_order.order_type == "long":
            order_type_flg = 1
        elif open_order.order_type == "short":
            order_type_flg = -1

        units = order_type_flg * open_order.units
        stop_loss_price = order_type_flg * round(
            order_type_flg * open_order.current_price
            - open_order.stop_loss_pips * pip_basis,
            pip_digit + 2,
        )
        take_profit_price = order_type_flg * round(
            order_type_flg * open_order.current_price
            + open_order.take_profit_pips * pip_basis,
            pip_digit + 2,
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
        if position_type == "long":
            data = {"longUnits": "ALL"}
        elif position_type == "short":
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

    stop_loss_pips = 10
    take_profit_pips = 10
    current_price = 115.111
    units = 10

    open_order = OpenOrderModel(
        instrument="USD_JPY",
        order_type="long",
        current_price=current_price,
        stop_loss_pips=stop_loss_pips,
        take_profit_pips=take_profit_pips,
        units=units,
    )
    print("------send orders------")
    print(open_order)
    # res = transaction.create_open_order_at_market(open_order)
    # print(res)

    print("------close position orders------")
    # res = transaction.close_current_position("USD_JPY", "long")
    # print(res)

    print("-------end of process-------")


if __name__ == "__main__":
    main()
