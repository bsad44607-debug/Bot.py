import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone


TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def get_gold_prices():
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        "GC=F?range=5d&interval=1h"
    )

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(req, timeout=20) as response:
        data = json.loads(response.read().decode())

    result = data["chart"]["result"][0]
    closes = [
        x for x in result["indicators"]["quote"][0]["close"]
        if x is not None
    ]

    return closes


def sma(values, period):
    return sum(values[-period:]) / period


def make_signal(prices):
    if len(prices) < 50:
        return "WAIT", "Not enough market data"

    price = prices[-1]
    ma20 = sma(prices, 20)
    ma50 = sma(prices, 50)

    if price > ma20 and ma20 > ma50:
        signal = "BUY"
        reason = "Price > MA20 > MA50"
    elif price < ma20 and ma20 < ma50:
        signal = "SELL"
        reason = "Price < MA20 < MA50"
    else:
        signal = "WAIT"
        reason = "Trend is unclear"

    return signal, reason


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": message
    }).encode()

    req = urllib.request.Request(url, data=data)

    with urllib.request.urlopen(req, timeout=20) as response:
        return response.read().decode()


def main():
    prices = get_gold_prices()
    signal, reason = make_signal(prices)

    price = prices[-1]
    ma20 = sma(prices, 20)
    ma50 = sma(prices, 50)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    message = (
        "🟡 XAUUSD AI SIGNAL\n\n"
        f"📊 Signal: {signal}\n"
        f"💰 Gold Price: {price:.2f}\n"
        f"📈 MA20: {ma20:.2f}\n"
        f"📉 MA50: {ma50:.2f}\n\n"
        f"🔎 Reason: {reason}\n"
        f"🕐 {now}\n\n"
        "⚠️ Signal is for analysis only. "
        "Always manage risk before trading."
    )

    send_telegram(message)


if __name__ == "__main__":
    main()
