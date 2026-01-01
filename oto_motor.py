import feedparser
import requests
import os

# --- AYARLAR ---
TOKEN = "8434933744:AAHkblFXXm5ibh8Bt6hKaMbaNMLvZUsPr90"
CHAT_ID = "1409453188"
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

ANAHTAR_KELIMELER = ["696 khk", "tediye", "memur zammı", "tayin", "becayiş", "işçi alımı", "mülakat", "promosyon"]
YT_IDS = [] # Takip etmek istediğin kanal ID'lerini buraya tırnak içinde ekleyebilirsin

def ai_ile_yorumla(baslik, ozet):
    if not OPENAI_KEY: return "Anahtar Yok"
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    prompt = f"Kamulog markası için şu haberi analiz et, 1 önemi, 1 reels başlığı, 1 soru yaz: {baslik} - {ozet}"
    data = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
    try:
        res = requests.post(url, headers=headers, json=data).json()
        return res['choices'][0]['message']['content']
    except: return "Analiz yapılamadı."

def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"})

def calistir():
    KAYNAKLAR = ["https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr", "https://www.resmigazete.gov.tr/rss/mevzuat.xml"]
    for yid in YT_IDS: KAYNAKLAR.append(f"https://www.youtube.com/feeds/videos.xml?channel_id={yid}")
    
    for url in KAYNAKLAR:
        feed = feedparser.parse(url)
        for haber in feed.entries:
            icerik = (haber.title + " " + haber.get('summary', '')).lower()
            if any(kelime in icerik for kelime in ANAHTAR_KELIMELER):
                yorum = ai_ile_yorumla(haber.title, haber.get('summary', ''))
                mesaj = f"🛰 <b>7/24 KAMULOG OTOMATİK RADAR</b>\n\n📰 <b>Haber:</b> {haber.title}\n\n🤖 <b>AI ANALİZİ:</b>\n{yorum}\n\n🔗 {haber.link}"
                telegram_gonder(mesaj)
                break # Her kaynaktan sadece en güncel eşleşeni alması için

if __name__ == "__main__":
    calistir()
