import streamlit as st

st.set_page_config(page_title="Kamulog X-Radar", page_icon="𝕏", layout="centered")

st.markdown("""
    <style>
    .stTextArea textarea { font-size: 22px !important; border: 2px solid #1DA1F2 !important; }
    .stButton button { height: 100px !important; font-size: 35px !important; background-color: #1DA1F2 !important; color: white !important; border-radius: 25px !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("𝕏 Kamulog Akıllı Takip Paneli")
st.write("Takip etmek istediğiniz X hesaplarını aşağıya yazın ve sistemi başlatın.")

# Takip Listesi Girişi
user_input = st.text_area("Hesap Kullanıcı Adları", height=250, placeholder="Örn:\nkamulog\nmemurlar\nresmigazete", help="Her satıra bir kullanıcı adı yazın.")

if st.button("🚀 SİSTEMİ BAŞLAT VE 7/24 TAKİP ET"):
    if user_input:
        with open("takip_listesi.txt", "w") as f:
            f.write(user_input)
        st.balloons()
        st.success("✅ Liste güncellendi! GitHub arka planda taramaya başladı.")
    else:
        st.warning("Lütfen en az bir hesap ismi girin.")
