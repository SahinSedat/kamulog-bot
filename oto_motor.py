import os
import requests
import feedparser

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def ai_analiz(text):
    if not OPENAI_KEY: return "AI Key Eksik"
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    prompt = f"Asagidaki X postunu Kamulog markasi icin analiz et. Ozetle, onemini belirt ve takipcilere sorulacak bir soru yaz:\n\n{text}"
    data = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
    try:
        res = requests.post(url, headers=headers, json=data).json()
        return res['choices'][0]['message']['content']
    except: return "Analiz yapilamadi."

def calistir():
    if not os.path.exists("takip_listesi.txt"): return
    
    with open("takip_listesi.txt", "r") as f:
        hesaplar = [line.strip() for line in f.readlines() if line.strip()]

    for hesap in hesaplar:
        # Nitter köprüsü (X verisine ulasmak icin)
        nitter_url = f"https://nitter.cz/{hesap}/rss"
        feed = feedparser.parse(nitter_url)
        
        for post in feed.entries[:1]: # En son postu al
            mesaj = f"𝕏 <b>YENİ POST: @{hesap}</b>\n\n📝 <b>Post:</b> {post.title}\n\n🤖 <b>AI ANALİZİ:</b>\n{ai_analiz(post.title)}\n\n🔗 {post.link}"
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          data={"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"})

if __name__ == "__main__":
    calistir()
