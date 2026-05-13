import requests
import time

TELEGRAM_TOKEN = "7419793459:AAGhSAzyDmg-7GFJrww0UXwYy2ia7N9m2jI"
CHAT_ID = "-5136013039"
APP_KEY = "534108"
APP_SECRET = "ilaCwDuzjSfpMqWjnh0UUSd4QfiHPchT"

from iop import IopClient, IopRequest

def get_products(keyword="phone"):
    client = IopClient("https://api-sg.aliexpress.com/sync", APP_KEY, APP_SECRET)
    request = IopRequest("aliexpress.affiliate.hotproduct.query")
    request.add_api_param("page_size", "5")
    request.add_api_param("target_currency", "USD")
    request.add_api_param("target_language", "EN")
    request.add_api_param("tracking_id", "default")
    response = client.execute(request)
    print("Response:", response.body[:300])
    products = []
    try:
        import json
        data = json.loads(response.body)
        items = data["aliexpress_affiliate_hotproduct_query_response"]["resp_result"]["result"]["products"]["product"]
        for item in items:
            products.append({
                "name": item["product_title"],
                "price": "$" + str(item["target_sale_price"]),
                "img": item["product_main_image_url"],
                "link": item["promotion_link"],
            })
    except Exception as e:
        print(f"Error: {e}")
    return products

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
        print(f"Error: {e}")

print("Bot starting...")
send_telegram("🤖 הבוט התחיל! מחפש דילים 🛍")
time.sleep(2)

sent = set()
while True:
    try:
        products = get_products()
        print(f"Found: {len(products)}")
        for p in products:
            if p["link"] not in sent:
                msg = (
                    f"🔥 <b>{p['name'][:100]}</b>\n"
                    f"💰 מחיר: <b>{p['price']}</b>\n"
                    f"🔗 <a href='{p['link']}'>לקנייה באלי אקספרס</a>"
                )
                send_telegram(msg, p["img"])
                sent.add(p["link"])
                time.sleep(5)
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(3600)
