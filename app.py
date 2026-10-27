import requests
import json
import os
from datetime import datetime
from curl_cffi import requests as cffi_requests

TELEGRAM_TOKEN = "8896973932:AAGjwZGGrQoTRr4Dz01JKM5zBT6ez5S7b0o"
CHAT_ID = "1027692313"
SOFASCORE_URL = "https://www.sofascore.com/api/v1/user-account/6758979fed09a67b595d5ba2"
KAYIT_DOSYASI = "gonderilen_tahminler.json"

def gonderilenleri_yukle():
    if os.path.exists(KAYIT_DOSYASI):
        with open(KAYIT_DOSYASI, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def gonderilenleri_kaydet(liste):
    with open(KAYIT_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(liste, f, ensure_ascii=False, indent=4)

def telegram_mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
    try:
        cffi_requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Telegram hata: {e}")

def veriyi_cek():
    headers = {
        "Host": "www.sofascore.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.sofascore.com/tr/user/profile/6758979fed09a67b595d5ba2",
    }
    try:
        session = cffi_requests.Session(impersonate="chrome")
        res = session.get(SOFASCORE_URL, headers=headers, timeout=15)
        print(f">>> Sofascore Status Code: {res.status_code}")
        if res.status_code == 200:
            return res.json()
        else:
            print(f">>> Sofascore beklenmeyen yanıt döndü: {res.text[:100]}")
            return None
    except Exception as e:
        print(f">>> Bağlantı hatasi: {e}")
        return None

if __name__ == "__main__":
    print(">>> Sofascore taranıyor...")
    veri = veriyi_cek()
    if veri:
        print(">>> Veri başarıyla çekildi!")
        # Buraya tahminleri kontrol edip Telegram'a gönderme mantığını ekleyebilirsin
    else:
        print(">>> Uyarı: Sofascore'dan veri çekilemedi!")
