import os

from oandapyV20 import API


class Config:
    TRADING_ENV = "live"  # or "practice"
    ACCESS_TOKEN = os.environ.get("OANDA_ACCESS_TOKEN")
    ACCOUNT_ID = os.environ.get("OANDA_ACCOUNT_ID")
    api = API(access_token=ACCESS_TOKEN, environment=TRADING_ENV)

    UNITS = 5000
    LOGFILE = "ichimoku.log"
