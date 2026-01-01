import os
import requests
import feedparser
import json
import hashlib
from datetime import datetime

# --- SİSTEM AYARLARI (GitHub Secrets) ---
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
APP_ID = "kamulog-elite-v1"

# --- HAFIZA VE AYAR DOSYALARI ---
SETTINGS_FILE = "takip_ayarlari.json"
SEEN_FILE = "gorulen_haberler.txt"

def ayarları_yükle():
    """Takip edilen kelimeleri ve hesapları dosyadan yükler."""
    varsayilan = {
        "kelimeler": ["696 khk", "tediye", "promosyon", "memur zammı", "becayiş", "tayin"],
        "hesaplar": ["SahinSedat", "kamulog"],
        "min_skor": 7  # 7 ve üzeri puanlı haberleri gönder
    }
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return varsayilan

def haber_goruldu_mu(haber_id):
    """Aynı haberin tekrar gönderilmesini engeller."""
    if not os.path.exists(SEEN_FILE): return False
    with open(SEEN_FILE, "r") as f:
        seen = f.read().splitlines()
    return haber_id in seen

def haberi_kaydet(haber_id):
    with open(SEEN_FILE, "a") as f:
        f.write(f"{haber_id}\n")

def ai_istihbarat_analizi(icerik):
    """OpenAI ile profesyonel içerik analizi ve puanlama yapar."""
    if not OPENAI_KEY: return None
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    
    prompt = f"""
    Sen Kamulog markasının Baş Stratejistisin. Aşağıdaki içeriği analiz et ve JSON formatında şu bilgileri ver:
    - skor: (0-10 arası önem puanı)
    - kategori: (Duyuru, Maaş, Atama, Mevzuat vb.)
    - ozet: (Tek cümlelik net özet)
    - reels_baslik: (Dikkat çekici kısa video başlığı)
    - video_kancası: (Videonun ilk 3 saniyesinde söylenecek çarpıcı cümle)
    - hashtagler: (En popüler 5 hashtag)
    - soru: (Takipçilere sorulacak etkileşim sorusu)
    
    İçerik: {icerik}
    
    Sadece JSON objesini döndür.
    """
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": { "type": "json_object" }
    }
    
    try:
        res = requests.post(url, headers=headers, json=data).json()
        return json.loads(res['choices'][0]['message']['content'])
    except: return None

def telegram_mesaj_gonder(mesaj, butonlar=None):
    """Zengin içerikli Telegram mesajı gönderir."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mesaj,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    if butonlar:
        payload["reply_markup"] = json.dumps({"inline_keyboard": butonlar})
    
    requests.post(url, data=payload)

def telegram_komut_isle():
    """Telegram'dan gelen yönetim komutlarını kontrol eder."""
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    try:
        res = requests.get(url).json()
        if not res.get("result"): return
        
        ayarlar = ayarları_yükle()
        degisiklik = False
        
        for update in res["result"]:
            msg = update.get("message", {}).get("text", "")
            if msg.startswith("/ekle"):
                k = msg.replace("/ekle", "").strip()
                if k and k not in ayarlar["kelimeler"]:
                    ayarlar["kelimeler"].append(k)
                    degisiklik = True
            elif msg.startswith("/sil"):
                k = msg.replace("/sil", "").strip()
                if k in ayarlar["kelimeler"]:
                    ayarlar["kelimeler"].remove(k)
                    degisiklik = True
        
        if degisiklik:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(ayarlar, f, ensure_ascii=False)
    except: pass

def calistir():
    telegram_komut_isle()
    ayarlar = ayarları_yükle()
    
    # Kaynak Havuzu
    kaynaklar = [
        "https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr",
        "https://www.resmigazete.gov.tr/rss/mevzuat.xml"
    ]
    
    # X (Twitter) Nitter Köprüleri
    bridges = ["https://nitter.privacydev.net", "https://nitter.poast.org", "https://nitter.moomoo.me"]
    for h in ayarlar["hesaplar"]:
        kaynaklar.append(f"{bridges[0]}/{h}/rss")

    for url in kaynaklar:
        try:
            feed = feedparser.parse(url)
            for haber in feed.entries[:5]:
                haber_id = hashlib.md5(haber.title.encode()).hexdigest()
                
                # Zaten gönderildiyse geç
                if haber_goruldu_mu(haber_id): continue
                
                # Kelime eşleşmesi var mı?
                eslesme = any(k.lower() in haber.title.lower() for k in ayarlar["kelimeler"])
                
                if eslesme:
                    # AI Analizi
                    analiz = ai_istihbarat_analizi(haber.title)
                    
                    if analiz and analiz.get("skor", 0) >= ayarlar["min_skor"]:
                        # Mesaj Tasarımı
                        puan_emoji = "🔥" if analiz['skor'] >= 9 else "📢"
                        mesaj = (
                            f"{puan_emoji} <b>[PUAN: {analiz['skor']}/10] - {analiz['kategori']}</b>\n"
                            f"──────────────────\n"
                            f"📰 <b>HABER:</b> {haber.title}\n\n"
                            f"📝 <b>ÖZET:</b> {analiz['ozet']}\n\n"
                            f"🎬 <b>REELS PLANI:</b>\n"
                            f"<b>• Başlık:</b> {analiz['reels_baslik']}\n"
                            f"<b>• Kanca:</b> {analiz['video_kancası']}\n\n"
                            f"💬 <b>SORU:</b> {analiz['soru']}\n\n"
                            f"🏷 <b>HASHTAG:</b> {analiz['hashtagler']}\n"
                            f"──────────────────\n"
                            f"🔗 <a href='{haber.link}'>Kaynağı Görüntüle</a>"
                        )
                        
                        butonlar = [
                            [{"text": "📁 Arşive Ekle", "callback_data": "arsiv"}, 
                             {"text": "❌ Takibi Bırak", "callback_data": f"sil_{haber_id}"}]
                        ]
                        
                        telegram_mesaj_gonder(mesaj, butonlar)
                        haberi_kaydet(haber_id)
                        break # Çok fazla mesaj yığılmasın diye
        except Exception as e:
            print(f"Hata: {e}")

if __name__ == "__main__":
    calistir()

