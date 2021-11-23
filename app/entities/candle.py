import dataclasses
from typing import List


@dataclasses.dataclass
class QuoteCurrentCandleModel:
    pass


@dataclasses.dataclass
class QuoteHistoricalCandleModel:
    granularity: str  # ["S5", "M1", "M15", "H1", "D"]
    instrument: str  # ["USD_JPY", "EUR_USD", "EUR_JPY"],
    price_type: str  # ["M", "A", "B"]
    quote_from: str  # yyyymmdd
    quote_to: str  # yyyymmdd
