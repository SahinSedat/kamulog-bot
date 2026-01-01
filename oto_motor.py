import os
import requests
import feedparser

# GitHub Secrets'tan verileri cek
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def ai_analiz(text):
    if not OPENAI_KEY: return "AI Key Hatasi"
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    prompt = f"Kamulog markasi icin bu postu analiz et, ozetle ve bir soru yaz: {text}"
    data = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
    try:
        res = requests.post(url, headers=headers, json=data).json()
        return res['choices'][0]['message']['content']
    except: return "Analiz yapilamadi."

def calistir():
    if not os.path.exists("takip_listesi.txt"): return
    with open("takip_listesi.txt", "r") as f:
        hesaplar = [line.strip() for line in f.readlines() if line.strip()]

    # En saglam 3 farkli X kopsunu deniyoruz
    bridges = ["https://nitter.privacydev.net", "https://nitter.poast.org", "https://nitter.moomoo.me"]

    for hesap in hesaplar:
        for bridge in bridges:
            try:
                feed = feedparser.parse(f"{bridge}/{hesap}/rss")
                if feed.entries:
                    post = feed.entries[0]
                    analiz = ai_analiz(post.title)
                    mesaj = f"𝕏 <b>@{hesap}</b>\n\n📝 {post.title}\n\n🤖 <b>AI:</b> {analiz}\n\n🔗 {post.link}"
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                  data={"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"})
                    break # Bir hesaptan mesaj gittiyse diger kopruye gerek yok
            except: continue

if __name__ == "__main__":
    calistir()