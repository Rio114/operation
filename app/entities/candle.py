import dataclasses
from typing import List


@dataclasses.dataclass
class QuoteCurrentCandleModel:
    granularity: str
    instrument: str
    price_type: str  # ["M", "A", "B"]
    stick_count: int


@dataclasses.dataclass
class QuoteHistoricalCandleModel:
    granularity: str
    instrument: str
    price_type: str  # ["M", "A", "B"]
    quote_from: str  # yyyymmdd
    quote_to: str  # yyyymmdd
