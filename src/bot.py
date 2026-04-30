from connection import connect, reconnect
from strategy import get_last_candle_direction
from executor import open_trade
from config import *

import time


def wait_for_fresh_candle(iq, pair):
    print(f"Waiting for fresh candle on {pair}...")
    current_from = iq.get_candles(pair, 60, 1, time.time())[0]["from"] 

    while True:
        latest_from = iq.get_candles(pair, 60, 1, time.time())[0]["from"]
        if latest_from > current_from:
            return latest_from
        time.sleep(0.05)


def resolve_trade_result(iq, trade_meta):
    pair = trade_meta["pair"]
    direction = trade_meta["direction"]
    entry_from = trade_meta["entry"]

    print(f"Waiting for candle close on {pair}...")

    while True:
        candles = iq.get_candles(pair, 60, 2, time.time())
        if candles[-1]["from"] > entry_from:
            break
        time.sleep(0.2)

    candles = iq.get_candles(pair, 60, 3, time.time())
    target = candles[-2]

    open_price = float(target["open"])
    close_price = float(target["close"])

    win = close_price > open_price if direction == "call" else close_price < open_price

    print("WIN" if win else "LOSS")
    return win


def get_next_direction_after_loss(step, direction):
    if step == 0 or step == 4:
        return "call" if direction == "put" else "put"
    return direction


def main():
    iq = connect()

    state = {
        "step": 0,
        "direction": None
    }

    wait_for_fresh_candle(iq, PAIR)

    while True:
        try:
            if state["direction"] is None:
                state["direction"] = get_last_candle_direction(iq, PAIR)

            step = state["step"]
            direction = state["direction"]
            amount = MARTINGALE[step]

            print(f"{PAIR} | {direction} | ${amount}")

            trade_id = None
            while trade_id is None:
                trade_id = open_trade(iq, PAIR, MARKET_TYPE, direction, amount)
                if trade_id is None:
                    time.sleep(RETRY_OPEN_DELAY)

            trade_meta = {
                "pair": PAIR,
                "direction": direction,
                "entry": time.time()
            }

            result = resolve_trade_result(iq, trade_meta)

            if result:
                state["step"] = 0
                state["direction"] = direction
            else:
                state["step"] += 1
                if state["step"] >= len(MARTINGALE):
                    state["step"] = 0
                    state["direction"] = get_last_candle_direction(iq, PAIR)
                else:
                    state["direction"] = get_next_direction_after_loss(step, direction)

        except Exception as e:
            print(f"Error: {e}")
            reconnect(iq)


if __name__ == "__main__":
    main()
