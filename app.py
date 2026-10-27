import os
import requests

# Telegram bot bilgileri (GitHub Secrets üzerinden çekilir)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

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

def check_predictions():
    # Buraya Sofascore veya ilgili kaynaktan verileri çeken 
    # ve yeni tahminleri kontrol eden mantığı ekleyebilirsin.
    # Örnek test bildirimi:
    print("Tahminler kontrol ediliyor...")
    
    # Yeni bir tahmin algılandığında aşağıdaki fonksiyon çağrılacak:
    # send_telegram_message("📢 *Yeni Tahmin Var!* \nDetaylar sistemde güncellendi.")

if __name__ == "__main__":
    check_predictions()
send_telegram_message("Test bildirimi")    
