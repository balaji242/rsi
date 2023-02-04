import pandas as pd
import time
import requests
from datetime import datetime
import calendar
import json


def retrieve_rsi(timeframe):
    # Define the Binance Futures API endpoint for retrieving exchange information
    endpoint = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    # Call the API to retrieve the exchange information
    response1 = requests.get(endpoint)
    # Parse the response into a Python dictionary
    exchange_info = json.loads(response1.text)
    # Extract the list of symbols from the exchange information
    symbols = [symbol["symbol"] for symbol in exchange_info["symbols"]]
    symbols_above_70 = []
    formatedsymbols = {}
    symbols_below_30 = []
    rsi_values_above_70 = {}
    rsi_values_below_30 = {}

    for symbol in symbols:
        timeinterval = timeframe

        now = datetime.utcnow()
        unixtime = calendar.timegm(now.utctimetuple())
        since = unixtime
        start = str(since - 60 * 60 * 10)

        url = 'https://fapi.binance.com/fapi/v1/klines?symbol=' + symbol + '&interval=' + str(
            timeinterval) + '&limit=100'
        data = requests.get(url).json()

        D = pd.DataFrame(data)
        D.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades',
                     'taker_base_vol', 'taker_quote_vol', 'is_best_match']

        period = 14
        df = D
        df['close'] = df['close'].astype(float)
        df2 = df['close'].to_numpy()

        df2 = pd.DataFrame(df2, columns=['close'])
        delta = df2.diff()

        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        _gain = up.ewm(com=(period - 1), min_periods=period).mean()
        _loss = down.abs().ewm(com=(period - 1), min_periods=period).mean()

        RS = _gain / _loss

        rsi = 100 - (100 / (1 + RS))
        rsi = rsi['close'].iloc[-1]
        rsi = round(rsi, 1)

        # Check if the RSI is above 75
        if rsi >= 70:
            symbols_above_70.append(symbol)
            rsi_values_above_70[f"{symbol}"] = rsi

        if rsi <= 30:
            if rsi != 0:
                symbols_below_30.append(symbol)
                rsi_values_below_30[symbol] = rsi

    # Print the symbols with an RSI above 70
    if symbols_above_70:
        for symbol in symbols_above_70:
            if symbol in rsi_values_above_70:
                formatedsymbols[symbol] = rsi_values_above_70[symbol]
            # return f"{symbol}: {rsi_values_above_70[symbol]}"
            else:

                formatedsymbols[symbol] = "does not exist in the rsi_values dictionary."
    else:
        formatedsymbols["-"] = "No symbols have an RSI above 70."

    # Print the symbols with an RSI below 30
    if symbols_below_30:
        for symbol in symbols_below_30:
            if symbol in rsi_values_below_30:
                formatedsymbols[symbol] = rsi_values_below_30[symbol]
                # return f"{symbol}: {rsi_values_below_30[symbol]}"
            else:
                formatedsymbols[symbol] = "does not exist in the rsi_values dictionary."

    else:
        formatedsymbols["-"] = "No symbols have an RSI below 30."

    return formatedsymbols
