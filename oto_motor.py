import os
import requests
import feedparser
from datetime import datetime

# GitHub Secrets'tan çekilen bilgiler
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def telegram_komutlarini_oku():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    try:
        response = requests.get(url).json()
        if not response.get("result"): 
            print("Telegram'dan yeni mesaj alınamadı.")
            return []
        
        yeni_kelimeler = []
        for update in response["result"]:
            mesaj_obj = update.get("message", {})
            mesaj_metni = mesaj_obj.get("text", "")
            
            if mesaj_metni.startswith("/ekle"):
                kelime = mesaj_metni.replace("/ekle", "").strip()
                if kelime and kelime not in yeni_kelimeler:
                    yeni_kelimeler.append(kelime)
                    print(f"Komut algılandı: {kelime}")
        
        return yeni_kelimeler
    except Exception as e:
        print(f"Telegram okuma hatası: {e}")
        return []

def calistir():
    # 1. Telegram'dan gelen komutları al
    ekstra_kelimeler = telegram_komutlarini_oku()
    
    # 2. Varsayılan listeyi oluştur/oku
    anahtar_kelimeler = ["696 khk", "tediye"] 
    if os.path.exists("takip_listesi.txt"):
        with open("takip_listesi.txt", "r") as f:
            anahtar_kelimeler.extend([l.strip() for l in f.readlines() if l.strip()])
    
    # Telegram'dan gelenleri ana listeye ekle
    anahtar_kelimeler.extend(ekstra_kelimeler)
    anahtar_kelimeler = list(set(anahtar_kelimeler)) # Tekrarları sil

    print(f"Şu an taranan kelimeler: {anahtar_kelimeler}")

    # 3. Tarama ve Gönderme (Örnek Google News)
    url = "https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr"
    feed = feedparser.parse(url)
    
    for haber in feed.entries[:10]:
        for kelime in anahtar_kelimeler:
            if kelime.lower() in haber.title.lower():
                mesaj = f"🛰 <b>RADAR YAKALADI: {kelime}</b>\n\n📰 {haber.title}\n\n🔗 {haber.link}"
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                              data={"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"})
                print(f"Haber gönderildi: {haber.title}")

if __name__ == "__main__":
    calistir()
