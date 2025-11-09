import requests
import time
import hmac
import hashlib
import base64
import json
from datetime import datetime
import os
import requests
from datetime import datetime

API_KEY = os.getenv("bg_def48d16c23a49f6cec440ab89ae4e08")
API_SECRET = os.getenv("8e850d67faa10deedfa0655ac355d3632d474ca502412b88810a1be9ecf91487")
API_PASSPHRASE = os.getenv("SelimBot123")


# Bitget ayarları
BASE_URL = "https://api.bitget.com"
SYMBOL = "AVAXUSDT"
MARGIN_MODE = "crossed"
LEVERAGE = 10
DRY_RUN = False  # True = sadece deneme, False = gerçek işlem

# ===================== #
# Bitget API Yardımcıları
# ===================== #

def bitget_request(method, path, body=None):
    timestamp = str(int(time.time() * 1000))
    body_str = json.dumps(body) if body else ""
    message = timestamp + method.upper() + path + body_str
    signature = base64.b64encode(
        hmac.new(API_SECRET.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
    ).decode()
    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "Content-Type": "application/json"
    }
    url = BASE_URL + path
    response = requests.request(method, url, headers=headers, data=body_str)
    return response.json()

# ===================== #
# Emir Fonksiyonları
# ===================== #

def open_order(side):
    """10x Long veya Short açar."""
    if DRY_RUN:
        print(f"[DRY RUN] {side} işlemi açılacaktı (10x).")
        return

    print(f"[BITGET] {side} işlemi açılıyor...")

    body = {
        "symbol": SYMBOL,
        "marginCoin": "USDT",
        "orderType": "market",
        "side": side,  # "open_long" veya "open_short"
        "size": "0.5",  # İşlem büyüklüğü (isteğe göre değiştir)
        "leverage": str(LEVERAGE)
    }
    result = bitget_request("POST", "/api/mix/v1/order/placeOrder", body)
    print("[BITGET Yanıtı]:", result)

# ===================== #
# TrendFlex Algo Kontrol
# ===================== #

def check_trendflex_signal():
    """TradingView webhook'tan sinyalleri okur (veya dosyadan simüle eder)."""
    try:
        with open("trendflex_signal.txt", "r") as f:
            signal = f.read().strip()
        return signal
    except FileNotFoundError:
        return None

# ===================== #
# Ana Döngü
# ===================== #

if __name__ == "__main__":
    print(f"[BOT] TrendFlex Algo 10x işlem botu başlatıldı | {SYMBOL} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    while True:
        signal = check_trendflex_signal()

        if signal == "openLong":
            open_order("open_long")
        elif signal == "openShort":
            open_order("open_short")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Henüz sinyal yok.")

        time.sleep(60)  # her 1 dakikada bir kontrol et
