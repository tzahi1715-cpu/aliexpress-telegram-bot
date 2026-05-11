import requests
import time
import json
from bs4 import BeautifulSoup
import os

TELEGRAM_TOKEN = "7419793459:AAGhSAzyDmg-7GFJrww0UXwYy2ia7N9m2jI"
CHAT_ID = "-5136013039"

def send_telegram(text, image_url=None):
    if image_url:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        data = {"chat_id": CHAT_ID, "photo": image_url, "caption": text, "parse_mode": "HTML"}
    else:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(url, data=data)

def get_deals():
    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://www.aliexpress.com/deals.html"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    products = []
    for item in soup.select(".deal-item")[:5]:
        try:
            name = item.select_one(".deal-item-title").text.strip()
            price = item.select_one(".price-current").text.strip()
            img = item.select_one("img")["src"]
            link = "https://www.aliexpress.com" + item.select_one("a")["href"]
            products.append({"name": name, "price": price, "img": img, "link": link})
        except:
            continue
    return products

sent = set()

while True:
    try:
        deals = get_deals()
        for p in deals:
            if p["link"] not in sent:
                msg = f"🛍 <b>{p['name']}</b>\n💰 מחיר: {p['price']}\n🔗 <a href='{p['link']}'>לקנייה באלי אקספרס</a>"
                send_telegram(msg, p["img"])
                sent.add(p["link"])
                time.sleep(2)
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(3600)
