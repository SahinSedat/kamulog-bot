import streamlit as st
import requests
import os
import feedparser

# --- AYARLAR ---
st.set_page_config(page_title="Kamulog X-Radar", layout="wide")

# Secrets'tan bilgileri çek (Hata vermemesi için kontrol et)
OPENAI_KEY = st.secrets.get("OPENAI_API_KEY", "")
TOKEN = st.secrets.get("TELEGRAM_TOKEN", "")
CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")

st.markdown("""
    <style>
    .main { background-color: #000000; color: white; }
    .stTextInput > div > div > input { font-size: 20px; height: 60px; }
    .stButton > button { height: 70px; width: 100%; font-size: 25px; background-color: #1DA1F2; color: white; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("𝕏 Kamulog İstihbarat Paneli")

# --- INPUT ALANI ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔗 Takip Edilecek X Hesapları")
    x_links = st.text_area("X Kullanıcı Adlarını gir (Her satıra bir tane, örn: kamulog)", 
                          height=150, help="Sadece kullanıcı adını yazman yeterli.")
    
    # Kelimeleri dosyaya kaydetme (GitHub Action okusun diye)
    if st.button("SİSTEMİ GÜNCELLE VE KAYDET"):
        with open("takip_listesi.txt", "w") as f:
            f.write(x_links)
        st.success("Takip listesi güncellendi! GitHub artık bu hesapları 7/24 tarayacak.")

with col2:
    st.info("🤖 **Yapay Zeka Durumu:** " + ("🟢 Aktif" if OPENAI_KEY else "🔴 Anahtar Eksik"))
    st.write("Bu panelden girdiğin hesaplar arka planda GitHub Actions tarafından her 30 dakikada bir kontrol edilir.")

# --- MANUEL TEST ---
if st.button("Hemen Şimdi Tara (Manuel)"):
    st.write("X hesapları taranıyor... (Nitter Bridge Aktif)")
    # Tarama fonksiyonu buraya gelecek
