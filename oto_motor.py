import os
import requests
import feedparser

# GitHub Secrets'tan çekilen bilgiler
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def ai_analiz(text):
    """Haber veya post içeriğini OpenAI ile analiz eder."""
    if not OPENAI_KEY: return "⚠️ AI Anahtarı (Secrets) bulunamadı."
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    
    # Senin için özelleştirilmiş analiz komutu
    prompt = f"""
    Sen Kamulog markasının yapay zeka asistanısın. Aşağıdaki içeriği analiz et:
    1. Bu içerik kamu çalışanları/işçileri için neden önemli?
    2. Instagram Reels için dikkat çekici bir başlık önerisi.
    3. Takipçilerin yorum yapmasını sağlayacak bir soru sor.
    
    İçerik: {text}
    """
    
    data = {
        "model": "gpt-4o-mini", 
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        res = requests.post(url, headers=headers, json=data).json()
        return res['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ AI Analiz Hatası: {str(e)}"

def telegram_komutlarini_oku():
    """Telegram'dan gelen /ekle komutlarını listeye dahil eder."""
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    ekstra_kelimeler = []
    try:
        res = requests.get(url).json()
        if res.get("result"):
            for update in res["result"]:
                msg = update.get("message", {}).get("text", "")
                if msg.startswith("/ekle"):
                    kelime = msg.replace("/ekle", "").strip()
                    if kelime: ekstra_kelimeler.append(kelime)
    except: pass
    return list(set(ekstra_kelimeler))

def calistir():
    # 1. Takip Listesini Oluştur
    takip_listesi = ["696 khk", "tediye", "promosyon", "memur zammı"] # Varsayılanlar
    
    # Telegram'dan gelen yeni kelimeleri ekle
    komutlar = telegram_komutlarini_oku()
    takip_listesi.extend(komutlar)
    
    # 2. Tarama Kaynakları (Google News + X Köprüleri)
    kaynaklar = ["https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr"]
    
    # Örnek X hesaplarını Nitter üzerinden ekle (Örn: Kamulog hesabı)
    hesaplar = ["SahinSedat", "kamulog"] 
    for h in hesaplar:
        kaynaklar.append(f"https://nitter.privacydev.net/{h}/rss")

    # 3. Tarama ve AI Analiz Süreci
    for url in kaynaklar:
        feed = feedparser.parse(url)
        for haber in feed.entries[:5]: # Her kaynaktan son 5 içerik
            icerik_metni = haber.title.lower()
            
            # Eğer içerikte takip ettiğimiz kelimelerden biri varsa
            if any(k.lower() in icerik_metni for k in takip_listesi):
                # Yapay Zekaya Yorumlat
                yorum = ai_analiz(haber.title)
                
                # Telegram'a Gönder
                mesaj = (
                    f"🛰 <b>KAMULOG AI RADAR</b>\n"
                    f"──────────────────\n"
                    f"📰 <b>İçerik:</b> {haber.title}\n\n"
                    f"🤖 <b>AI ANALİZİ:</b>\n{yorum}\n\n"
                    f"🔗 <a href='{haber.link}'>Kaynağa Git</a>"
                )
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                              data={"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"})
                break # Aynı haberi tekrar tarama

if __name__ == "__main__":
    calistir()

