import os
import json
import time
import threading
import urllib.request
from datetime import datetime
from curl_cffi import requests
from flask import Flask

app = Flask(__name__)

# --- SENİN AYARLARIN ---
TELEGRAM_TOKEN = "8896973932:AAGjwZGGrqoTRr4DzO1JKM5zBt6ez5S7bOo"
CHAT_ID = "1027692313"
SOFASCORE_URL = "https://www.sofascore.com/api/v1/user-account/6758979fed09a67b595d5ba2"
KAYIT_DOSYASI = "gonderilen_tahminler.json"
KONTROL_SURESI = 300  # 5 dakika

@app.route('/')
def home():
    return "Scuti Tahmin Takip Botu 7/24 Aktif Çalışıyor!"

def gonderilenleri_yukle():
    if os.path.exists(KAYIT_DOSYASI):
        try:
            with open(KAYIT_DOSYASI, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def gonderilenleri_kaydet(kayit_seti):
    with open(KAYIT_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(list(kayit_seti), f)

def telegram_mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    veri = json.dumps({
        "chat_id": CHAT_ID,
        "text": mesaj,
        "parse_mode": "HTML"
    }).encode("utf-8")
    
    req = urllib.request.Request(
        url, 
        data=veri, 
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.status == 200
    except Exception as e:
        print(f"Telegram gönderim hatası: {e}")
        return False

def veriyi_cek():
    headers = {
        "Host": "www.sofascore.com",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:158.0) Gecko/20100101 Firefox/158.0",
        "Accept": "*/*",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://www.sofascore.com/tr/user/profile/6758979fed09a67b595d5ba2",
        "Cookie": "__gads=ID=a33774a0e8980c9c:T=1792942648:RT=1793120264:S=ALNI_MY976Rieain66y_Tok-P36rauopKA; __gpi=UID=0000155c46c0e19c:T=1792942648:RT=1793120264:S=ALNI_Mbo3Xw6Z_PJExAWfHyiO6_rLMHOxQ; __eoi=ID=0f5e613656d5028a:T=1792942648:RT=1793120264:S=AA-AfjaV5Lh6z6Rf8s7jAcc3eger; cto_bundle=bYo67181T0F2QkJOQ3lRRFIwUkFpZyUyQktjMkxWdVE3V1B3emNGZEpSUTlkRDlLZ3k4MlIyeVV6ZnlnYW1uOSUyQm94JTJGT29Xc1RVdXJudk50JTJCek91UURYbDBJTGVyNldKb3Y3UTN0JTJCcmM3MW5wSHROcXhrTWslMkZBOVhUcHdIaGZBRXpzS1VrTiUyRiUyRjR0TDVaRjdjbGd5cG13cjFLZzJiNWY1c1pWU0V5N1djMnpYQTVQSHlFZ2RSWmkzV0ZrR3ptNTVGeWx3Y3Zh; _gcl_au=1.1.1855409508.1792942667; _ga_HNQ9P9MGZR=GS2.1.s1793119895$o33$g1$t1793121884$j53$l0$h0; _ga=GA1.1.453990442.1792942667; g_state={\"i_l\":1,\"i_ll\":1792942710401,\"i_b\":\"hABHEmEfNmGp2B3APM7qpASwnstdGSc4OVcFIqT8mrY\",\"i_e\":{\"enable_itp_optimization\":24},\"i_et\":1792942710401}; FCCDCF=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B32%2C%22%5B%5C%22069049f4-2615-4b82-ad3b-2b10f5599002%5C%22%2C%5B1792942643%2C796000000%5D%5D%22%5D%5D%5D; FCNEC=%5B%5B%22AKsRol_oJKVMLzRjhBlftxvY_H5WXZFJyPecliYavkEDo6rFKCy-pVVkIRDxHo9d1I3SwBkWYTIIxMSnE0Uoa_xDcZZ3wajdqUfAmadsyemd8oGGhFtQNDxRcXne6hVcsr9d144cMF0nMwUC6yhh2lyYoVjSKKj6Tg%3D%3D%22%5D%5D",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=4",
        "Cache-Control": "max-age=0"
    }
    try:
        session = requests.Session(impersonate="chrome")
        res = session.get(SOFASCORE_URL, headers=headers, timeout=15)
        print(f">>> Sofascore Status Code: {res.status_code}", flush=True)
        
        if res.status_code == 200:
            return res.json()
        else:
            print(f">>> Sofascore beklenmeyen yanıt döndü: {res.text[:100]}", flush=True)
            return None
    except Exception as e:
        print(f">>> Bağlantı hatasi: {e}", flush=True)
        return None

def tahminleri_kontrol_et():
    print(">>> Arka plan döngüsü başlatıldı!", flush=True)
    while True:
        try:
            print(">>> Sofascore taranıyor...", flush=True)
            gonderilenler = gonderilenleri_yukle()
            veri = veriyi_cek()

            if not veri:
                print(">>> UYARI: Sofascore'dan veri çekilemedi (Boş döndü veya engellendi)!", flush=True)

            if veri:
                tahmin_listesi = veri.get("predictions", [])
                print(f">>> {len(tahmin_listesi)} adet tahmin bulundu, kontrol ediliyor...", flush=True)
                for item in reversed(tahmin_listesi):
                    mac_id = str(item.get("eventId"))
                    if mac_id and mac_id not in gonderilenler:
                        ev_sahibi = item.get("homeTeamName", "Bilinmiyor")
                        deplasman = item.get("awayTeamName", "Bilinmiyor")
                        tahmin = item.get("vote", "-")
                        oran = item.get("odds", {}).get("decimalValue", "-")
                        spor = item.get("sportSlug", "football")
                        
                        ts = item.get("startDateTimestamp")
                        mac_zamani = datetime.fromtimestamp(ts).strftime("%d.%m.%Y - %H:%M") if ts else "Belirtilmemiş"

                        if tahmin == "1":
                            tahmin_detay = f"1 ({ev_sahibi} Kazanır)"
                        elif tahmin == "2":
                            tahmin_detay = f"2 ({deplasman} Kazanır)"
                        elif tahmin == "X":
                            tahmin_detay = "X (Beraberlik)"
                        else:
                            tahmin_detay = tahmin

                        spor_ikon = "⚽" if spor == "football" else "🏀" if spor == "basketball" else "🎾"

                        mesaj = (
                            f"🔔 <b>Scuti. Yeni Tahmin Girdi!</b>\n\n"
                            f"{spor_ikon} <b>Maç:</b> {ev_sahibi} - {deplasman}\n"
                            f"🕒 <b>Tarih/Saat:</b> {mac_zamani}\n"
                            f"🎯 <b>Tahmin:</b> {tahmin_detay}\n"
                            f"📈 <b>Oran:</b> {oran}"
                        )
                        
                        if telegram_mesaj_gonder(mesaj):
                            gonderilenler.add(mac_id)
                            gonderilenleri_kaydet(gonderilenler)
                        
                        time.sleep(1)
        except Exception as e:
            print(f">>> Hata döngüsü: {e}", flush=True)
            
        time.sleep(KONTROL_SURESI)

# Arka planda tahminleri kontrol edecek döngüyü başlatıyoruz
t = threading.Thread(target=tahminleri_kontrol_et)
t.daemon = True
t.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
