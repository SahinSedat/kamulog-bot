import os
import requests
import feedparser

# --- AYARLAR ---
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def telegram_mesaj_gonder(metin):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": metin, "parse_mode": "HTML"})

def telegram_komutlari_dinle():
    """Telegram'dan gelen /ekle, /takip gibi komutları kontrol eder."""
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    res = requests.get(url).json()
    if not res.get("result"): return
    
    for update in res["result"]:
        msg = update.get("message", {}).get("text", "")
        if msg.startswith("/ekle "): # Kelime ekle
            kelime = msg.replace("/ekle ", "").strip()
            with open("kelimeler.txt", "a") as f: f.write(f"\n{kelime}")
            telegram_mesaj_gonder(f"✅ Kelime eklendi: {kelime}")
        elif msg.startswith("/takip "): # X veya YT hesabı ekle
            hesap = msg.replace("/takip ", "").strip()
            with open("hesaplar.txt", "a") as f: f.write(f"\n{hesap}")
            telegram_mesaj_gonder(f"✅ Takip listesine eklendi: {hesap}")

def ai_yorumla(metin):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    prompt = f"Sen Kamulog stratejistisin. Bu içeriği analiz et, önemini yaz ve etkileşim sorusu sor: {metin}"
    data = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
    try:
        res = requests.post(url, headers=headers, json=data).json()
        return res['choices'][0]['message']['content']
    except: return "Analiz yapılamadı."

def tarama_yap():
    # Kelimeleri ve hesapları oku
    kelimeler = open("kelimeler.txt").read().splitlines() if os.path.exists("kelimeler.txt") else ["tediye", "khk"]
    hesaplar = open("hesaplar.txt").read().splitlines() if os.path.exists("hesaplar.txt") else []

    kaynaklar = ["https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr", "https://www.resmigazete.gov.tr/rss/mevzuat.xml"]
    
    for h in hesaplar:
        if h:
            # X (Twitter) için Nitter
            kaynaklar.append(f"https://nitter.poast.org/{h}/rss")
            # YouTube için (ID ise)
            kaynaklar.append(f"https://www.youtube.com/feeds/videos.xml?channel_id={h}")

    for url in kaynaklar:
        feed = feedparser.parse(url)
        for entry in feed.entries[:2]:
            icerik = (entry.title + " " + entry.get("summary", "")).lower()
            if any(k.lower() in icerik for k in kelimeler if k):
                yorum = ai_yorumla(entry.title)
                msg = f"🛰 <b>KAMULOG AI RADAR</b>\n\n📌 <b>Kaynak:</b> {url[:30]}...\n📰 <b>İçerik:</b> {entry.title}\n\n🤖 <b>AI:</b> {yorum}\n\n🔗 {entry.link}"
                telegram_mesaj_gonder(msg)

if __name__ == "__main__":
    telegram_komutlari_dinle()
    tarama_yap()
