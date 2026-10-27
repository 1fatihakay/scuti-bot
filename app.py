import os
import json
import requests
from curl_cffi import requests as curl_requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SEEN_FILE = "gonderilen_tahminler.json"

SOFASCORE_URL = os.getenv("SOFASCORE_URL", "https://www.sofascore.com/api/v1/user-account/.../predictions")

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram token veya chat ID eksik!")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Telegram mesajı başarıyla gönderildi.")
    else:
        print(f"Mesaj gönderilemedi: {response.text}")

def load_seen_matches():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_seen_matches(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=4)

def veriyi_cek():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Origin": "https://www.sofascore.com",
        "Referer": "https://www.sofascore.com/"
    }
    try:
        session = curl_requests.Session(impersonate="chrome110")
        response = session.get(SOFASCORE_URL, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Bağlantı hatası, durum kodu: {response.status_code}")
            return None
    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return None

def check_predictions():
    print("Tahminler kontrol ediliyor...")
    gonderilenler = load_seen_matches()
    veri = veriyi_cek()
    
    if not veri:
        print("Veri alınamadı.")
        return

    try:
        tahmin_listesi = veri.get('predictions', [])
        for item in tahmin_listesi:
            tahmin_id = str(item.get('id', item.get('match', {}).get('id')))
            
            if tahmin_id not in gonderilenler:
                spor = item.get('sport', {}).get('name', 'Spor')
                ev_sahibi = item.get('match', {}).get('homeTeam', {}).get('name', 'Ev Sahibi')
                deplasman = item.get('match', {}).get('awayTeam', {}).get('name', 'Deplasman')
                oran = item.get('odd', '')
                tahmin_detay = item.get('prediction', '')

                mesaj = (
                    f"📢 *Yeni Tahmin Geldi!*\n\n"
                    f"⚽ *Spor:* {spor}\n"
                    f"🏠 *Maç:* {ev_sahibi} - {deplasman}\n"
                    f"🎯 *Tahmin:* {tahmin_detay}\n"
                    f"📊 *Oran:* {oran}"
                )
                
                send_telegram_message(mesaj)
                gonderilenler.append(tahmin_id)
        
        save_seen_matches(gonderilenler)
    except Exception as e:
        print(f"Veri işleme hatası: {e}")

if __name__ == "__main__":
    check_predictions()
