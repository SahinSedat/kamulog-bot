import os
import requests
import feedparser

# GitHub Secrets'tan çekilir
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def ai_analiz(post_text):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    prompt = f"Aşağıdaki X postunu Kamulog markası için analiz et. Uzunsa özetle, önemini belirt ve bir etkileşim sorusu yaz:\n\n{post_text}"
    data = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
    try:
        res = requests.post(url, headers=headers, json=data).json()
        return res['choices'][0]['message']['content']
    except: return "Analiz başarısız."

def calistir():
    if not os.path.exists("takip_listesi.txt"): return
    
    with open("takip_listesi.txt", "r") as f:
        hesaplar = [line.strip() for line in f.readlines() if line.strip()]

    for hesap in hesaplar:
        # X hesaplarını Nitter üzerinden RSS olarak çekiyoruz (X kısıtlamasını aşmak için)
        nitter_url = f"https://nitter.net/{hesap}/rss"
        feed = feedparser.parse(nitter_url)
        
        for post in feed.entries[:2]: # Her hesaptan son 2 postu al
            baslik = post.title
            link = post.link
            analiz = ai_analiz(baslik)
            
            mesaj = f"𝕏 <b>YENİ POST: @{hesap}</b>\n\n📝 <b>Post:</b> {baslik}\n\n🤖 <b>AI ANALİZİ:</b>\n{analiz}\n\n🔗 {link}"
            
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          data={"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"})

if __name__ == "__main__":
    calistir()
