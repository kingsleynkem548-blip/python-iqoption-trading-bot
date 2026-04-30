def get_last_candle_direction(iq, pair):
    candles = iq.get_candles(pair, 60, 3, __import__("time").time())
    last = candles[-2]
    return "call" if float(last["close"]) > float(last["open"]) else "put"
