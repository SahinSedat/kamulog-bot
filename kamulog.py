import streamlit as st
import feedparser
import time
import requests
from datetime import datetime
import pandas as pd

# --- KİMLİK BİLGİLERİ ---
TOKEN = "8434933744:AAHkblFXXm5ibh8Bt6hKaMbaNMLvZUsPr90"
CHAT_ID = "1409453188"

# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="Kamulog Haber Paneli", layout="wide")
st.title("🤖 Kamulog Haber & Sosyal Medya Radarı")

# --- SOL PANEL: AYARLAR ---
st.sidebar.header("⚙️ Ayarlar")
anahtar_kelimeler_input = st.sidebar.text_area("Takip Edilecek Kelimeler (Virgülle ayır)",
    "696 KHK, memur, işçi zammı, tediye, becayiş, atama, resmi gazete, belediye şirketi")
ANAHTAR_KELIMELER = [x.strip().lower() for x in anahtar_kelimeler_input.split(",")]

youtube_kanallari = st.sidebar.text_area("Takip Edilecek YouTube Kanal ID'leri",
    "UCxxxxxxxxxxxxxxx") # Buraya kanal ID'leri gelecek

# --- FONKSİYONLAR ---
def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
    requests.post(url, data=payload)

def haberleri_tara():
    bulunanlar = []
    RSS_URLS = [
        "https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr",
        "https://www.resmigazete.gov.tr/rss/mevzuat.xml"
    ]
    
    # YouTube Kanallarını Ekle (ID varsa)
    for k_id in youtube_kanallari.split(","):
        if k_id.strip():
            RSS_URLS.append(f"https://www.youtube.com/feeds/videos.xml?channel_id={k_id.strip()}")

    for url in RSS_URLS:
        feed = feedparser.parse(url)
        for haber in feed.entries:
            icerik = (haber.title + " " + haber.get('summary', '')).lower()
            for kelime in ANAHTAR_KELIMELER:
                if kelime in icerik:
                    bulunanlar.append({
                        "Zaman": datetime.now().strftime("%H:%M"),
                        "Kaynak": "YouTube" if "youtube.com" in url else "Haber Portalı",
                        "Başlık": haber.title,
                        "Link": haber.link,
                        "Kelime": kelime
                    })
                    break
    return bulunanlar

# --- ANA EKRAN ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📡 Canlı Akış")
    if st.button("Şimdi Tara"):
        sonuclar = haberleri_tara()
        if sonuclar:
            df = pd.DataFrame(sonuclar)
            st.table(df)
            for s in sonuclar:
                msg = f"🛰 <b>RADAR YAKALADI!</b>\n\n📝 {s['Başlık']}\n🔗 {s['Link']}"
                telegram_gonder(msg)
        else:
            st.info("Yeni bir haber bulunamadı.")

with col2:
    st.subheader("💡 İçerik Fikirleri")
    st.write("Burada yakalanan haberlere göre yapay zeka önerileri görünecek.")

# Otomatik Tarama Döngüsü Bilgisi
st.sidebar.info("Otomatik tarama için bu sayfayı açık tutmalısın.")
