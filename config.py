import os

BITGET = {
    "API_KEY": os.getenv("bg_def48d16c23a49f6cec440ab89ae4e08"),
    "API_SECRET": os.getenv("8e850d67faa10deedfa0655ac355d3632d474ca502412b88810a1be9ecf91487"),
    "API_PASSPHRASE": os.getenv("SelimBot123")
}

TELEGRAM = {
    "TOKEN": os.getenv("TOKEN")
}

DRY_RUN = False   # Gerçek işlem yerine test modu (True yaparsan test olur)
POLL_SECS = 30    # Her 30 saniyede bir sinyal kontrol eder
