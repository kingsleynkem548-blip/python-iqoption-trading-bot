import time
from config import EXPIRY_MINUTES

def open_trade(iq, pair, market_type, direction, amount):
    try:
        if market_type == "digital":
            success, trade_id = iq.buy_digital_spot(pair, amount, direction, EXPIRY_MINUTES)
        else:
            success, trade_id = iq.buy(amount, pair, direction, EXPIRY_MINUTES)

        if success:
            return trade_id
    except Exception as e:
        print(f"Trade error: {e}")

    return None
