import time
import requests
from datetime import datetime
from trendflex_algo import check_trendflex_signal as get_trendflex_signal


from config import BITGET, TELEGRAM, DRY_RUN, POLL_SECS
import hmac, hashlib, json
import requests

SYMBOL = BITGET["SYMBOL"]
LEVERAGE = BITGET["LEVERAGE"]
ORDER_SIZE = BITGET["ORDER_SIZE"]

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM['TOKEN']}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM["CHAT_ID"], "text": text}, timeout=10)
        print("[TELEGRAM]", text)
    except Exception as e:
        print("Telegram send error:", e)

def bitget_order(side, size, leverage):
    if DRY_RUN:
        print(f"[DRY RUN] {side} {size} {SYMBOL} x{leverage}")
        return
    url = "https://api.bitget.com/api/mix/v1/order/place"
    timestamp = str(int(time.time() * 1000))
    params = {
        "symbol": SYMBOL,
        "price": "0",  # Market order
        "size": size,
        "side": side,
        "type": "market",
        "leverage": leverage
    }
    msg = timestamp + 'POST' + '/api/mix/v1/order/place' + json.dumps(params)
    sign = hmac.new(BITGET["API_SECRET"].encode(), msg.encode(), hashlib.sha256).hexdigest()
    headers = {
        "ACCESS-KEY": BITGET["API_KEY"],
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": BITGET["PASSPHRASE"],
        "Content-Type": "application/json"
    }
    r = requests.post(url, headers=headers, data=json.dumps(params))
    print("Bitget response:", r.json())

LAST_SIGNAL = None
LAST_SIGNAL_TS = 0

if __name__ == "__main__":
    send_telegram(f"[BOT] TrendFlex watcher başladı: {SYMBOL} | DRY_RUN={DRY_RUN} | {datetime.now()}")
    print("TrendFlex bot çalışıyor...", SYMBOL)
    while True:
        try:
            signal = get_trendflex_signal(SYMBOL)  # "BUY"/"SELL"/None
            now = time.time()
            if signal and signal != LAST_SIGNAL:
                if now - LAST_SIGNAL_TS < 30:  # Debounce
                    print("debounce skip")
                else:
                    LAST_SIGNAL = signal
                    LAST_SIGNAL_TS = now
                    if signal == "BUY":
                        send_telegram(f"📈 AL SİNYALİ ({SYMBOL}) — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        bitget_order("buy", ORDER_SIZE, LEVERAGE)
                    elif signal == "SELL":
                        send_telegram(f"📉 SAT SİNYALİ ({SYMBOL}) — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        bitget_order("sell", ORDER_SIZE, LEVERAGE)
            else:
                print(f"[{datetime.now()}] Henüz sinyal yok.")
        except Exception as e:
            print("Loop error:", e)
            try:
                send_telegram(f"[ERROR] TrendFlex bot hata: {e}")
            except:
                pass
        time.sleep(POLL_SECS)



