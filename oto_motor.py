import os
import requests
import feedparser

# GitHub Secrets'tan çekilen bilgiler
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def telegram_komutlarini_oku():
    """Telegram'dan gelen son /ekle komutunu okur ve listeye ekler."""
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    try:
        updates = requests.get(url).json()
        if not updates["result"]: return
        
        # Sadece son mesajı kontrol et
        son_guncelleme = updates["result"][-1]
        mesaj = son_guncelleme.get("message", {}).get("text", "")
        
        if mesaj.startswith("/ekle"):
            yeni_kelime = mesaj.replace("/ekle", "").strip()
            if yeni_kelime:
                # Dosyaya ekle (Hafıza)
                with open("takip_listesi.txt", "a") as f:
                    f.write(f"\n{yeni_kelime}")
                
                # Onay mesajı gönder
                onay_mesajı = f"✅ '{yeni_kelime}' kelimesi takip listesine eklendi ve tarama başlıyor!"
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                              data={"chat_id": CHAT_ID, "text": onay_mesajı})
    except Exception as e:
        print(f"Komut okuma hatası: {e}")

def ai_analiz(text):
    if not OPENAI_KEY: return "AI Anahtarı Bulunamadı."
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    prompt = f"Kamulog markası için bu haberi analiz et, özetle ve etkileşim sorusu yaz: {text}"
    data = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
    try:
        res = requests.post(url, headers=headers, json=data).json()
        return res['choices'][0]['message']['content']
    except: return "Analiz yapılamadı."

def calistir():
    # Önce Telegram'dan yeni bir komut gelmiş mi bak ve varsa listeyi güncelle
    telegram_komutlarini_oku()

    if not os.path.exists("takip_listesi.txt"):
        with open("takip_listesi.txt", "w") as f: f.write("kamulog") # Varsayılan

    with open("takip_listesi.txt", "r") as f:
        kelimeler = [line.strip() for line in f.readlines() if line.strip()]

    # Tarama Motoru (Google News + X Köprüleri)
    kaynaklar = ["https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr"]
    bridges = ["https://nitter.privacydev.net", "https://nitter.poast.org"]

    for kelime in kelimeler:
        # Önce haber sitelerinde ara
        feed = feedparser.parse(kaynaklar[0])
        for haber in feed.entries[:5]: # Son 5 habere bak
            if kelime.lower() in haber.title.lower():
                analiz = ai_analiz(haber.title)
                mesaj = f"🛰 <b>RADAR YAKALADI: {kelime}</b>\n\n📰 {haber.title}\n\n🤖 <b>AI:</b> {analiz}\n\n🔗 {haber.link}"
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                              data={"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"})

if __name__ == "__main__":
    calistir()
