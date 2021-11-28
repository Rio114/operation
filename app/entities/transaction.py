import dataclasses
from typing import List


@dataclasses.dataclass
class PositionModel:
    # TODO: fix to get datetime
    id: int  # the first of trade_ids
    trade_ids: List[int]
    instrument: str
    position_type: str
    average_price: float
    units: int
    unrealized_profit_loss: float


@dataclasses.dataclass
class OpenOrderModel:
    instrument: str
    order_type: str
    current_price: float
    stop_loss_price: float
    take_profit_price: float
    units: int


@dataclasses.dataclass
class CloseOrderModel:
    id: int
    position_id: int
    order_type: str
    price: float
