from app.config import Config
from app.entities.candle import QuoteCurrentCandleModel
from app.infra.api.candle import Candle
from app.infra.api.transaction import Transaction
from app.logic.ichimoku_method import IchimokuMethod


	
import yaml

def main():
    config = Config()
    instruments = ["USD_JPY", "EUR_JPY", "EUR_USD"]
    granularity = "M15"
    units = config.UNITS

    with open('app/ichimoku_params.yml', 'r') as yml:
        ichimoku_params = yaml.load(yml)

    transaction_client = Transaction()
    positions = transaction_client.find_current_positions()
    print("------current positions------")
    print(positions)

    for instrument in instruments:
        params = ichimoku_params[instrument]
        stop_loss = params['STOP']
        take_profit = params['PROFIT']
        short = params['ICHIMOKU'][0]
        long = params['ICHIMOKU'][1]
        longlong = params['ICHIMOKU'][2]
    
    quote_client = Candle()
    qccm = QuoteCurrentCandleModel(
        granularity=granularity,
        instrument=instrument,
        price_type="M",
        stick_count=longlong,
    )

    logic = IchimokuMethod(short, long, longlong)
    df = quote_client.quote_latest_candles(qccm)
    df_judgment = logic.generate_judgment_matrix(df)
    print(
        df_judgment.iloc[:-longlong][["time", "buy_judgment", "sell_judgment"]].iloc[-1]
    )


if __name__ == "__main__":
    main()
