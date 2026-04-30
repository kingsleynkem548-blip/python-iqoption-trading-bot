import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

PAIR = "EURUSD-OTC"
MARKET_TYPE = "binary"
ACCOUNT_TYPE = "PRACTICE"

MARTINGALE = [1.2, 2.6, 5.6, 12, 26, 56, 120, 260]

EXPIRY_MINUTES = 1
RETRY_OPEN_DELAY = 2
