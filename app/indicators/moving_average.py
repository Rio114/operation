import pandas as pd


class MovingAverage:
    def __init__(self):
        pass

    def sma(self, se: pd.Series, length: int) -> pd.Series:
        return se.rolling(length).mean()
