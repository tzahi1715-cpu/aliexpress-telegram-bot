import requests
import time
import os

TELEGRAM_TOKEN = "7419793459:AAGhSAzyDmg-7GFJrww0UXwYy2ia7N9m2jI"
CHAT_ID = "-5136013039"

def send_telegram(text, image_url=None):
    try:
        if image_url:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            data = {"chat_id": CHAT_ID, "photo": image_url, "caption": text, "parse_mode": "HTML"}
        else:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
        requests.post(url, data=data)
        print("Message sent!")
    except Exception as e:
        print(f"Telegram error: {e}")

def get_deals():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    products = []
    keywords = ["phone case", "led light", "smart watch", "earbuds", "power bank"]
    for kw in keywords:
        try:
            url = f"https://www.aliexpress.com/wholesale?SearchText={kw.replace(' ','+')}&SortType=total_tranpro_desc"
            r = requests.get(url, headers=headers, timeout=10)
            if "aliexpress" in r.url:
                products.append({
                    "name": f"🔥 {kw.title()} - Best Sellers",
                    "price": "Check price",
                    "img": None,
                    "link": url
                })
        except Exception as e:
            print(f"Error: {e}")
    return products

# Test message on startup
send_telegram("🤖 הבוט התחיל לעבוד! ממתין לדילים מאלי אקספרס...")

sent = set()
while True:
    try:
        deals = get_deals()
        for p in deals:
            if p["link"] not in sent:
                msg = f"🛍 <b>{p['name']}</b>\n💰 {p['price']}\n🔗 <a href='{p['link']}'>לקנייה באלי אקספרס</a>"
                send_telegram(msg, p.get("img"))
                sent.add(p["link"])
                time.sleep(3)
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(3600)
