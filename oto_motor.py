import os
import requests
import feedparser
import json
import hashlib
from datetime import datetime

# --- AYARLAR (GitHub Secrets) ---
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- TAKİP LİSTESİ ---
# GitHub Actions her seferinde sıfırlandığı için kelimeleri buradan yönetebilirsin
ANAHTAR_KELIMELER = ["696 khk", "tediye", "promosyon", "memur zammı", "becayiş", "tayin", "işçi alımı", "atama"]
X_HESAPLAR = ["SahinSedat", "kamulog"]

def ai_istihbarat_analizi(icerik):
    """OpenAI ile içerik analizi yapar. Hata payı bırakmaz."""
    if not OPENAI_KEY: return None
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    
    prompt = f"""
    Sen Kamulog markasının Baş Stratejistisin. Aşağıdaki haberi analiz et. 
    Lütfen şu formatta cevap ver (JSON DEĞİL, DÜZ METİN):
    SKOR: (0-10 arası önem)
    ÖZET: (Kısa özet)
    REELS: (Video başlığı)
    KANCA: (İlk cümle)
    SORU: (Etkileşim sorusu)
    HASHTAG: (#kamulog #memur vb.)

    Haber: {icerik}
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
        print(f"AI Hatası: {e}")
        return "⚠️ Analiz sırasında teknik bir sorun oluştu."

def telegram_gonder(mesaj):
    """Telegram'a mesajı iletir."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML", "disable_web_page_preview": False}
    try:
        requests.post(url, data=payload)
    except: pass

def calistir():
    print(f"--- Tarama Basladi: {datetime.now()} ---")
    
    # Kaynaklar
    kaynaklar = [
        "https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr",
        "https://www.resmigazete.gov.tr/rss/mevzuat.xml"
    ]
    
    # X Hesaplarını Nitter üzerinden ekle
    # Nitter köprüleri bazen kapalı olabilir, en sağlamlarını ekledik
    bridges = ["https://nitter.privacydev.net", "https://nitter.poast.org"]
    for h in X_HESAPLAR:
        kaynaklar.append(f"{bridges[0]}/{h}/rss")

    for url in kaynaklar:
        try:
            feed = feedparser.parse(url)
            # Sadece en güncel 3 habere bak (Hız ve kota için)
            for haber in feed.entries[:3]:
                baslik = haber.title.lower()
                
                # Kelime Eşleşmesi Kontrolü
                if any(k in baslik for k in ANAHTAR_KELIMELER):
                    print(f"Eşleşme Bulundu: {haber.title}")
                    
                    # AI Analizi Al
                    analiz = ai_istihbarat_analizi(haber.title)
                    
                    # Mesaj Tasarımı
                    mesaj = (
                        f"🛰 <b>KAMULOG AI İSTİHBARAT</b>\n"
                        f"──────────────────\n"
                        f"📰 <b>HABER:</b> {haber.title}\n\n"
                        f"🤖 <b>AI ANALİZİ VE STRATEJİ:</b>\n{analiz}\n\n"
                        f"🔗 <a href='{haber.link}'>Kaynağa Git</a>"
                    )
                    
                    telegram_gonder(mesaj)
                    # Bir kaynaktan bir tane göndermesi için break
                    break 
        except Exception as e:
            print(f"Kaynak Hatası ({url}): {e}")

if __name__ == "__main__":
    calistir()

