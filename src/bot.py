import time
import os
from dotenv import load_dotenv
from iqoptionapi.stable_api import IQ_Option

# ================= LOAD ENV =================
load_dotenv()
EMAIL = os.getenv("Email") # Enter registered email
PASSWORD = os.getenv("Password") # Enter registered password

# ================= CONFIG =================
PAIR = "EURUSD-OTC"        # Example: "EURUSD-OTC" or "EURUSD"
MARKET_TYPE = "binary"     # Options: "digital" or "binary"
ACCOUNT_TYPE = "PRACTICE"

# Martingale sequence
MARTINGALE = [1.2, 2.6, 5.6, 12, 26, 56, 120, 260]

# Trade settings
EXPIRY_MINUTES = 1
RETRY_OPEN_DELAY = 2

# ================= NOTES =================
# Credentials are loaded securely from environment variables.
# Do NOT hardcode sensitive information in this file.
# ==========================================

# ================= CONNECT =================
print("Connecting to IQ Option...")
Iq = IQ_Option(EMAIL, PASSWORD)
Iq.connect()
Iq.change_balance(ACCOUNT_TYPE)
print(f"✅ Connected | Balance: {Iq.get_balance()}")
time.sleep(5)

# ================= FUNCTIONS =================

def reconnect():
    try:
        print("🔄 Reconnecting...")
        Iq.connect()
        Iq.change_balance(ACCOUNT_TYPE)
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Reconnect failed: {e}")

def get_last_candle_direction(pair):
    try:
        candles = Iq.get_candles(pair, 60, 3, time.time())
        last = candles[-2]
        return "call" if float(last["close"]) > float(last["open"]) else "put"
    except Exception as e:
        print(f"⚠️ Could not read last candle direction: {e}")
        return "call"

def wait_for_fresh_candle(pair):
    print(f"⏳ Waiting for fresh candle on {pair}...")
    current_from = Iq.get_candles(pair, 60, 1, time.time())[0]["from"]
    while True:
        latest_from = Iq.get_candles(pair, 60, 1, time.time())[0]["from"]
        if latest_from > current_from:
            return latest_from
        time.sleep(0.05)

def open_trade(pair, market_type, direction, amount):
    """
    Trade ONLY the exact market you manually selected.
    market_type: "digital" or "binary"
    """
    print(f"🚀 OPENING → {pair} | {market_type.upper()} | {direction.upper()} | ${amount}")

    try:
        entry_candle = Iq.get_candles(pair, 60, 1, time.time())[0]

        if market_type == "digital":
            success, trade_id = Iq.buy_digital_spot(pair, amount, direction, EXPIRY_MINUTES)
            print(f"[DIGITAL] success={success}, id={trade_id}")
        else:
            success, trade_id = Iq.buy(amount, pair, direction, EXPIRY_MINUTES)
            print(f"[BINARY] success={success}, id={trade_id}")

        if success:
            return {
                "trade_id": trade_id,
                "pair_used": pair,
                "direction": direction,
                "amount": amount,
                "entry_candle_from": entry_candle["from"],
                "market_type": market_type,
            }

    except Exception as e:
        print(f"[{market_type.upper()} ERROR] {e}")

    print("❌ Trade could not be opened")
    return None

def resolve_trade_result(trade_meta):
    """
    Candle-based result check for the exact market traded.
    """
    pair_used = trade_meta["pair_used"]
    direction = trade_meta["direction"]
    entry_candle_from = trade_meta["entry_candle_from"]

    print(f"⏳ Waiting for trade candle to close on {pair_used}...")

    while True:
        candles = Iq.get_candles(pair_used, 60, 2, time.time())
        newest_from = candles[-1]["from"]
        if newest_from > entry_candle_from:
            break
        time.sleep(0.2)

    time.sleep(0.5)

    candles = Iq.get_candles(pair_used, 60, 3, time.time())
    target = None

    for candle in candles:
        if candle["from"] == entry_candle_from:
            target = candle
            break

    if target is None:
        target = candles[-2]

    open_price = float(target["open"])
    close_price = float(target["close"])

    print(f"📊 Trade Candle ({pair_used}) → Open: {open_price}, Close: {close_price}")

    if direction == "call":
        win = close_price > open_price
    else:
        win = close_price < open_price

    print("💰 WIN" if win else "❌ LOSS")
    return win

def get_next_direction_after_loss(step_just_lost, direction_just_lost):
    """
    Your exact sequence:
    - 1.2 loss -> 2.6 opposite
    - 2.6, 5.6, 12, 26 losses -> same direction
    - 26 loss -> 56 opposite
    - 56, 120, 260 losses -> same direction
    """
    if step_just_lost == 0:
        return "call" if direction_just_lost == "put" else "put"

    if step_just_lost == 4:
        return "call" if direction_just_lost == "put" else "put"

    return direction_just_lost

# ================= STATE =================
state = {
    "step": 0,
    "direction": None,
    "locked_market": MARKET_TYPE,
}

print("\nStarting manual-market bot...\n")

# First candle sync
wait_for_fresh_candle(PAIR)

# ================= MAIN LOOP =================
while True:
    try:
        if state["step"] < 0 or state["step"] >= len(MARTINGALE):
            state["step"] = 0

        if state["direction"] is None:
            state["direction"] = get_last_candle_direction(PAIR)

        current_step = state["step"]
        current_direction = state["direction"]
        amount = MARTINGALE[current_step]

        print(f"\n⏱ {time.strftime('%H:%M:%S')}")
        print(f"Pair: {PAIR}")
        print(f"Market Type: {MARKET_TYPE.upper()}")
        print(f"Direction: {current_direction.upper()} | Amount: ${amount} | Step: {current_step}")

        trade_meta = None
        while trade_meta is None:
            trade_meta = open_trade(PAIR, MARKET_TYPE, current_direction, amount)
            if trade_meta is None:
                print(f"Retrying in {RETRY_OPEN_DELAY}s...")
                time.sleep(RETRY_OPEN_DELAY)

        result = resolve_trade_result(trade_meta)

        direction_just_traded = trade_meta["direction"]
        step_just_traded = current_step

        if result:
            print("🔁 WIN → RESET TO 1.2")
            state["step"] = 0
            state["direction"] = direction_just_traded
            print(f"➡️ Next: {MARTINGALE[state['step']]} {state['direction'].upper()}")
            time.sleep(1)
            continue

        print("❌ LOSS → ADVANCE SEQUENCE")
        state["step"] = step_just_traded + 1

        if state["step"] >= len(MARTINGALE):
            print("🛑 260 lost → reset sequence")
            state["step"] = 0
            state["direction"] = get_last_candle_direction(PAIR)
            time.sleep(1)
            continue

        state["direction"] = get_next_direction_after_loss(
            step_just_traded,
            direction_just_traded
        )

        print(f"➡️ Next Amount: {MARTINGALE[state['step']]}")
        print(f"➡️ Next Direction: {state['direction'].upper()}")

        time.sleep(1)

    except Exception as e:
        print(f"⚠️ Main loop error: {e}")
        reconnect()
        time.sleep(2)
