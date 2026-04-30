import time
from iqoptionapi.stable_api import IQ_Option
from config import EMAIL, PASSWORD, ACCOUNT_TYPE

def connect():
    print("Connecting to IQ Option...")
    iq = IQ_Option(EMAIL, PASSWORD)
    iq.connect()
    iq.change_balance(ACCOUNT_TYPE)
    print(f"Connected | Balance: {iq.get_balance()}")
    time.sleep(2)
    return iq

def reconnect(iq):
    try:
        print("Reconnecting...")
        iq.connect()
        iq.change_balance(ACCOUNT_TYPE)
        time.sleep(2)
    except Exception as e:
        print(f"Reconnect failed: {e}")
