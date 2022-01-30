import time

import yaml
from app.config import Config
from app.infra.api.candle import Candle
from app.infra.api.transaction import Transaction
from app.logic.ichimoku_method import IchimokuMethod
from app.logic.ichimoku_method_dynamic_stop import IchimokuMethodDynamicStop
from app.tasks import get_module_logger
from app.tasks.trade import trade


def exec():
    logger = get_module_logger(__name__)

    with open("app/ichimoku_params.yaml", "r") as yml:
        ichimoku_params = yaml.safe_load(yml)

    transaction_client = Transaction()
    positions = transaction_client.find_current_positions()

    logger.info("------current positions------")

    position_units = {}
    for position in positions:
        position_units[position.instrument] = position.units

    logger.info(position_units)
    quote_client = Candle()

    instrument = "USD_JPY"
    trade(
        IchimokuMethod,
        instrument,
        transaction_client,
        quote_client,
        position_units,
        ichimoku_params,
    )

    ### dynamic stop
    instrument = "EUR_JPY"
    trade(
        IchimokuMethodDynamicStop,
        instrument,
        transaction_client,
        quote_client,
        position_units,
        ichimoku_params,
    )


if __name__ == "__main__":
    exec()
