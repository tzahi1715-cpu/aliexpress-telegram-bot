import requests
import time
import hashlib

TELEGRAM_TOKEN = "7419793459:AAE0mSRGuNituAJDZ5wdmplG5F8VsLpZGHQ"
CHAT_ID = "-5136013039"
APP_KEY = "534108"
APP_SECRET = "2nSUuI2T0IfFwvNb1TpAmpeILtsjCszH"
USD_TO_ILS = 3.7

def translate_to_hebrew(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "en", "tl": "he", "dt": "t", "q": text[:200]}
        r = requests.get(url, params=params, timeout=10)
        return r.json()[0][0][0]
    except:
        return text

def translate_to_english(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "he", "tl": "en", "dt": "t", "q": text[:200]}
        r = requests.get(url, params=params, timeout=10)
        return r.json()[0][0][0]
    except:
        return text

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
    products = []
    try:
        data = r.json()
        items = data["aliexpress_affiliate_product_query_response"]["resp_result"]["result"]["products"]["product"]
        for item in items:
            name_he = translate_to_hebrew(item["product_title"])
            price_usd = float(item["target_sale_price"])
            price_ils = round(price_usd * USD_TO_ILS, 2)
            products.append({
                "name": name_he,
                "price": f"₪{price_ils}",
                "img": item["product_main_image_url"],
                "link": item["promotion_link"],
            })
    except Exception as e:
        print(f"Parse error: {e}")
    return products

def send_telegram(text, image_url=None, chat_id=None):
    cid = chat_id or CHAT_ID
    try:
        if image_url:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            data = {"chat_id": cid, "photo": image_url, "caption": text, "parse_mode": "HTML"}
        else:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            data = {"chat_id": cid, "text": text, "parse_mode": "HTML"}
        r = requests.post(url, data=data)
        print("Telegram:", r.status_code)
    except Exception as e:
        print(f"Error: {e}")

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    r = requests.get(url, params=params, timeout=35)
    return r.json().get("result", [])

def handle_messages(offset):
    updates = get_updates(offset)
    for update in updates:
        offset = update["update_id"] + 1
        try:
            msg = update.get("message", {})
            text = msg.get("text", "")
            chat_id = msg["chat"]["id"]
            if text and not text.startswith("/"):
                send_telegram(f"🔍 מחפש: <b>{text}</b>...", chat_id=chat_id)
                keyword_en = translate_to_english(text)
                products = get_products(keyword_en)
                if products:
                    for p in products:
                        msg_text = (
                            f"🛍 <b>{p['name']}</b>\n"
                            f"💰 מחיר: <b>{p['price']}</b>\n"
                            f"🔗 <a href='{p['link']}'>לקנייה באלי אקספרס</a>"
                        )
                        send_telegram(msg_text, p["img"], chat_id=chat_id)
                        time.sleep(2)
                else:
                    send_telegram("😔 לא נמצאו מוצרים, נסה מילת חיפוש אחרת.", chat_id=chat_id)
        except Exception as e:
            print(f"Handle error: {e}")
    return offset

print("Starting...")
send_telegram("🤖 הבוט התחיל!\n\nשלח לי מילת חיפוש ואמצא לך מוצרים מאלי אקספרס 🛍\nלדוגמא: שרשרת זהב, תיק עור, טבעת כסף")
time.sleep(2)

keywords = [
    "gold necklace women", "silver bracelet", "pearl earrings",
    "ring women jewelry", "anklet bracelet", "hair accessories women",
    "crystal necklace", "charm bracelet", "vintage earrings",
    "wedding jewelry set", "boho jewelry", "statement necklace",
    "women handbag", "shoulder bag women", "crossbody bag",
    "tote bag women", "mini bag women", "luxury bag women",
    "clutch bag evening", "backpack women fashion", "wallet women leather",
]
ki = 0
sent = set()
offset = None
last_auto = time.time()

while True:
    try:
        offset = handle_messages(offset)
        if time.time() - last_auto >= 3600:
            kw = keywords[ki % len(keywords)]
            print(f"Auto searching: {kw}")
            products = get_products(kw)
            for p in products:
                if p["link"] not in sent:
                    msg = (
                        f"🛍 <b>{p['name']}</b>\n"
                        f"💰 מחיר: <b>{p['price']}</b>\n"
                        f"🔗 <a href='{p['link']}'>לקנייה באלי אקספרס</a>"
                    )
                    send_telegram(msg, p["img"])
                    sent.add(p["link"])
                    time.sleep(5)
            ki += 1
            last_auto = time.time()
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(10)
