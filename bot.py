import requests
import time
import hashlib

TELEGRAM_TOKEN = "7419793459:AAGzaJezfM6Xqe8U3JWbYWnGbkYLEoV-pzA"
CHAT_ID = "-5136013039"
APP_KEY = "534108"
APP_SECRET = "2nSUuI2T0IfFwvNb1TpAmpeILtsjCszH"

def sign(params):
    s = APP_SECRET
    for k in sorted(params.keys()):
        s += str(k) + str(params[k])
    s += APP_SECRET
    return hashlib.md5(s.encode("utf-8")).hexdigest().upper()

def get_products(keyword):
    ts = str(int(time.time() * 1000))
    params = {
        "app_key": APP_KEY,
        "timestamp": ts,
        "sign_method": "md5",
        "method": "aliexpress.affiliate.product.query",
        "keywords": keyword,
        "page_size": "5",
        "page_no": "1",
        "target_currency": "USD",
        "target_language": "EN",
        "tracking_id": "default",
        "sort": "SALE_PRICE_ASC",
    }
    params["sign"] = sign(params)
    r = requests.post("https://api-sg.aliexpress.com/sync", data=params, timeout=20)
    print("Response:", r.text[:400])
    products = []
    try:
        data = r.json()
        items = data["aliexpress_affiliate_product_query_response"]["resp_result"]["result"]["products"]["product"]
        for item in items:
            products.append({
                "name": item["product_title"],
                "price": "$" + str(item["target_sale_price"]),
                "img": item["product_main_image_url"],
                "link": item["promotion_link"],
            })
    except Exception as e:
        print(f"Parse error: {e}")
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
        print("Telegram:", r.status_code)
    except Exception as e:
        print(f"Error: {e}")

print("Starting...")
send_telegram("🤖 הבוט התחיל! מחפש דילים 🛍")
time.sleep(2)

keywords = ["earbuds", "smart watch", "power bank", "led strip", "phone case"]
ki = 0
sent = set()

while True:
    try:
        kw = keywords[ki % len(keywords)]
        print(f"Searching: {kw}")
        products = get_products(kw)
        print(f"Found: {len(products)}")
        for p in products:
            if p["link"] not in sent:
                msg = (
                    f"🛍 <b>{p['name'][:100]}</b>\n"
                    f"💰 מחיר: <b>{p['price']}</b>\n"
                    f"🔗 <a href='{p['link']}'>לקנייה באלי אקספרס</a>"
                )
                send_telegram(msg, p["img"])
                sent.add(p["link"])
                time.sleep(5)
        ki += 1
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(3600)
