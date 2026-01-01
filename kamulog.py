import streamlit as st
import feedparser
import time
import requests
from datetime import datetime
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Kamulog AI Control Panel", layout="wide", page_icon="🚀")

# --- KİMLİK BİLGİLERİ (Telegram) ---
TOKEN = "8434933744:AAHkblFXXm5ibh8Bt6hKaMbaNMLvZUsPr90"
CHAT_ID = "1409453188"

# --- ARAYÜZ (Görsel Düzenleme) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton>button { background-color: #ff4b4b; color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛰 Kamulog Yapay Zeka Haber Merkezi")
st.sidebar.title("Yönetim Paneli")

# --- GİRDİ ALANLARI ---
openai_key = st.sidebar.text_input("OpenAI API Anahtarı (sk-...)", type="password")

with st.sidebar.expander("🔍 Takip Ayarları", expanded=True):
    keywords_raw = st.text_area("Anahtar Kelimeler (Virgülle ayır)",
        "696 KHK, tediye, memur zammı, tayin, becayiş, işçi alımı, mülakat, promosyon")
    ANAHTAR_KELIMELER = [x.strip().lower() for x in keywords_raw.split(",")]

with st.sidebar.expander("📺 YouTube & Sosyal Medya"):
    yt_ids_raw = st.text_area("YouTube Kanal ID'leri (Virgülle ayır)")
    YT_IDS = [x.strip() for x in yt_ids_raw.split(",") if x.strip()]

# --- FONKSİYONLAR ---

def ai_ile_yorumla(haber_basligi, haber_ozeti):
    if not openai_key:
        return "⚠️ OpenAI API Key girilmedi."
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_key}"
    }
    
    prompt = f"""
    Sen Kamulog markasının sosyal medya stratejistisin. 
    Aşağıdaki haberi analiz et ve Sedat'a (Kamulog sahibi) şu 3 şeyi kısa ve öz yaz:
    1. Bu haber kamu işçileri/memurlar için neden kritik?
    2. Instagram/Reels için bomba bir video başlığı önerisi.
    3. Takipçilere sorulacak, yorum sayısını artıracak o soru nedir?

    Haber: {haber_basligi}
    Özet: {haber_ozeti}
    """
    
    data = {
        "model": "gpt-4o-mini", # En mantıklı seçim budur
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=data).json()
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ AI Hatası: {str(e)}"

def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
    requests.post(url, data=payload)

def tarama_yap():
    st.write("🔎 Tarama başlatıldı...")
    bulunan_haberler = []
    KAYNAKLAR = [
        "https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr",
        "https://www.resmigazete.gov.tr/rss/mevzuat.xml"
    ]
    
    # YouTube Kanallarını Ekle
    for yid in YT_IDS:
        KAYNAKLAR.append(f"https://www.youtube.com/feeds/videos.xml?channel_id={yid}")

    for url in KAYNAKLAR:
        feed = feedparser.parse(url)
        for haber in feed.entries:
            baslik = haber.title.lower()
            ozet = haber.get('summary', '').lower()
            icerik = baslik + " " + ozet
            
            for kelime in ANAHTAR_KELIMELER:
                if kelime in icerik:
                    # AI Yorumunu Al
                    st.write(f"✅ Yakalandı: {haber.title[:50]}...")
                    yorum = ai_ile_yorumla(haber.title, haber.get('summary', 'Özet yok'))
                    
                    mesaj = (
                        f"🛰 <b>KAMULOG AI RADAR</b>\n"
                        f"──────────────────\n"
                        f"📰 <b>Haber:</b> {haber.title}\n\n"
                        f"🤖 <b>AI ANALİZİ:</b>\n{yorum}\n\n"
                        f"🔗 <a href='{haber.link}'>Kaynağa Git</a>"
                    )
                    
                    telegram_gonder(mesaj)
                    bulunan_haberler.append({"Zaman": datetime.now().strftime("%H:%M"), "Haber": haber.title})
                    break
    return bulunan_haberler

# --- ANA EKRAN BUTONLARI ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 Manuel Tara ve Telegram'a Gönder"):
        sonuclar = tarama_yap()
        if sonuclar:
            st.success(f"{len(sonuclar)} yeni içerik bulundu!")
            st.table(pd.DataFrame(sonuclar))
        else:
            st.warning("Eşleşen yeni bir haber bulunamadı.")

with col2:
    st.info("💡 **İpucu:** Sol tarafa OpenAI keyini girdikten sonra 'Tara' butonuna basarsan analizler gelmeye başlar.")

# Bilgilendirme
st.divider()
st.write("⚠️ **Not:** GitHub üzerinden Streamlit Cloud'a bağladıysan, bu sayfa kapalıyken otomatik tarama yapması için koda 'loop' eklenmelidir. Şu an manuel tetikleme ile çalışır.")
