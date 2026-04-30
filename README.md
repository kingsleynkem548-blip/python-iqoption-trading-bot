# Python IQ Option Trading Bot

A modular Python-based automated trading bot built for IQ Option, featuring real-time trade execution, candle analysis, and a custom martingale risk management system.

---

## 🚀 Features

* Automated trade execution using IQ Option API
* Candle-based market direction analysis
* Custom martingale strategy with directional logic
* Real-time trade monitoring and result resolution
* Reconnection handling for unstable API sessions
* Modular code structure for scalability and maintainability

---

## 🧠 Strategy Overview

The bot uses a **candle-direction strategy** combined with a **custom martingale system**:

* Initial trade direction is based on the previous candle
* On first loss → direction flips
* On subsequent losses → direction persistence logic applies
* Full martingale ladder:
  `1.2 → 2.6 → 5.6 → 12 → 26 → 56 → 120 → 260`
* Sequence resets after a win

---

## ⚙️ Project Structure

```
src/
├── bot.py           # Main execution loop
├── config.py        # Environment variables & settings
├── connection.py    # API connection logic
├── strategy.py      # Trade direction logic
├── executor.py      # Trade execution logic
```

---

## 🔐 Environment Setup

Create a `.env` file in your root directory:

```
EMAIL=your_email_here
PASSWORD=your_password_here
```

---

## ▶️ How to Run

1. Install dependencies:

```
pip install -r requirements.txt
```

2. Run the bot:

```
python src/bot.py
```

---

## ⚠️ Disclaimer

This project is for educational and research purposes only.
Trading financial instruments involves risk. Use at your own discretion.

---

## 📌 Author

Built and maintained by Kingsley Nkem
