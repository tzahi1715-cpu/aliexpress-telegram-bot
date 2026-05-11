import requests
import time
import hashlib
import hmac

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
        r = requests.post(url, data=data)
        print("Sent:", r.status_code)
    except Exception as e:
        print(f"Telegram error: {e}")

def get_deals():
    keywords = ["earbuds", "smart watch", "phone case", "led strip", "power bank"]
    products = []
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)"}
    
    for kw in keywords:
        try:
            url = f"https://www.aliexpress.com/wholesale?SearchText={kw.replace(' ','+')}"
            r = requests.get(url, headers=headers, timeout=15)
            
            import re
            imgs = re.findall(r'"imageUrl":"(//ae01\.alicdn\.com[^"]+)"', r.text)
            titles = re.findall(r'"title":"([^"]{10,80})"', r.text)
            prices = re.findall(r'"minPrice":(\d+\.?\d*)', r.text)
            ids = re.findall(r'"productId":"(\d+)"', r.text)
            
            if imgs and titles and ids:
                img = "https:" + imgs[0]
                title = titles[0]
                price = prices[0] if prices else "?"
                pid = ids[0]
                link = f"https://www.aliexpress.com/item/{pid}.html"
                products.append({"name": title, "price": f"${price}", "img": img, "link": link})
        except Exception as e:
            print(f"Error {kw}: {e}")
    return products

send_telegram("🤖 הבוט התחיל! מחפש דילים...")

sent = set()
while True:
    try:
        deals = get_deals()
        for p in deals:
            if p["link"] not in sent:
                msg = f"🛍 <b>{p['name']}</b>\n💰 מחיר: {p['price']}\n🔗 <a href='{p['link']}'>לקנייה באלי אקספרס</a>"
                send_telegram(msg, p.get("img"))
                sent.add(p["link"])
                time.sleep(3)
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(3600)
