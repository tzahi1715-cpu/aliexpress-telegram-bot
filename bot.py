import requests
import time
import hashlib
import re

TELEGRAM_TOKEN = "7419793459:AAE0mSRGuNituAJDZ5wdmplG5F8VsLpZGHQ"
CHAT_ID = "-5136013039"
APP_KEY = "534108"
APP_SECRET = "2nSUuI2T0IfFwvNb1TpAmpeILtsjCszH"
USD_TO_ILS = 3.7
MIN_PRICE_ILS = 20
MIN_RATING = 4.0
MIN_DISCOUNT = 20

DICTIONARY = {
    "כובע": "hat", "כובע צמר": "wool hat beanie", "כובע קש": "straw hat",
    "שרשרת": "necklace", "שרשרת זהב": "gold necklace",
    "שרשרת פנינים": "pearl necklace", "שרשרת כסף": "silver necklace",
    "טבעת": "ring", "טבעת זהב": "gold ring", "טבעת כסף": "silver ring",
    "עגיל": "earring", "עגילים": "earrings", "עגילי פנינים": "pearl earrings",
    "צמיד": "bracelet", "צמיד זהב": "gold bracelet", "צמיד כסף": "silver bracelet",
    "תיק": "handbag", "תיק עור": "leather handbag", "תיק יד": "handbag",
    "תיק גב": "backpack", "תיק צד": "crossbody bag",
    "ארנק": "wallet", "נעליים": "shoes", "נעלי עקב": "high heels",
    "כפכפים": "sandals", "נעלי ספורט": "sneakers",
    "נעלי בית": "slippers", "נעלי בית לגבר": "men slippers",
    "נעלי בית לאישה": "women slippers", "נעליים לגבר": "men shoes",
    "נעלי ספורט לגבר": "men sneakers", "שמלה": "dress",
    "חולצה": "shirt", "מעיל": "coat", "צעיף": "scarf",
    "כפפות": "gloves", "משקפי שמש": "sunglasses",
    "שעון": "watch", "שעון חכם": "smart watch",
    "שעון לגבר": "men watch", "שעון לאישה": "women watch",
    "אוזניות": "earbuds wireless", "טלפון": "phone case",
    "מטען": "power bank", "תכשיטים": "jewelry",
    "אביזרים": "accessories", "סיכה": "brooch",
    "קליפס": "hair clips", "גומי שיער": "hair ties",
    "חולצה לגבר": "men shirt", "מכנסיים לגבר": "men pants",
    "גרביים לגבר": "men socks", "חגורה לגבר": "men belt",
    "ארנק לגבר": "men wallet", "כובע לגבר": "men hat",
    "מעיל לגבר": "men jacket", "כובע לאישה": "women hat",
    "ארנק לאישה": "women wallet",
}

COLORS = {
    "זהב": "gold", "כסף": "silver", "שחור": "black", "לבן": "white",
    "אדום": "red", "כחול": "blue", "ירוק": "green", "ורוד": "pink",
    "סגול": "purple", "חום": "brown", "אפור": "gray", "צהוב": "yellow",
}

URGENCY_PHRASES = [
    "⏰ מלאי מוגבל - הזדרז!",
    "🔥 נמכר בקצב מטורף!",
    "⚡ הצעה לזמן מוגבל!",
    "🏃 אל תפספס את המחיר הזה!",
    "💎 עסקה שאי אפשר לסרב לה!",
]

def get_urgency():
    import random
    return random.choice(URGENCY_PHRASES)

def translate_to_hebrew(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "en", "tl": "he", "dt": "t", "q": text[:200]}
        r = requests.get(url, params=params, timeout=10)
        return r.json()[0][0][0]
    except:
        return text

def translate_to_english(text):
    result = ""
    if text in DICTIONARY:
        result = DICTIONARY[text]
    else:
        for key in DICTIONARY:
            if key in text:
                result = DICTIONARY[key]
                break
    if not result:
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {"client": "gtx", "sl": "he", "tl": "en", "dt": "t", "q": text[:200]}
            r = requests.get(url, params=params, timeout=10)
            result = r.json()[0][0][0]
        except:
            result = text
    if "לגבר" in text and "men" not in result:
        result = "men " + result
    elif "לאישה" in text and "women" not in result:
        result = "women " + result
    for he_color, en_color in COLORS.items():
        if he_color in text and en_color not in result:
            result = result + " " + en_color
            break
    return result

def parse_price_range(text):
    match = re.search(r'(\d+)\s*-\s*(\d+)\s*שח', text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

def sign(params):
    s = APP_SECRET
    for k in sorted(params.keys()):
        s += str(k) + str(params[k])
    s += APP_SECRET
    return hashlib.md5(s.encode("utf-8")).hexdigest().upper()

def get_products(keyword, min_price=None, max_price=None):
    ts = str(int(time.time() * 1000))
    params = {
        "app_key": APP_KEY,
        "timestamp": ts,
        "sign_method": "md5",
        "method": "aliexpress.affiliate.product.query",
        "keywords": keyword,
        "page_size": "20",
        "page_no": "1",
        "target_currency": "USD",
        "target_language": "EN",
        "tracking_id": "default",
        "sort": "SALE_PRICE_DESC",
    }
    params["sign"] = sign(params)
    r = requests.post("https://api-sg.aliexpress.com/sync", data=params, timeout=20)
    products = []
    try:
        data = r.json()
        items = data["aliexpress_affiliate_product_query_response"]["resp_result"]["result"]["products"]["product"]
        for item in items:
            price_usd = float(item["target_sale_price"])
            price_ils = round(price_usd * USD_TO_ILS, 2)
            if price_ils < MIN_PRICE_ILS:
                continue
            if min_price and price_ils < min_price:
                continue
            if max_price and price_ils > max_price:
                continue
            rating = float(item.get("evaluate_rate", "0").replace("%", "") or 0) / 20
            if rating > 0 and rating < MIN_RATING:
                continue
            discount = int(item.get("discount", "0") or 0)
            if discount < MIN_DISCOUNT:
                continue
            name_he = translate_to_hebrew(item["product_title"])
            products.append({
                "name": name_he,
                "price": f"₪{price_ils}",
                "img": item["product_main_image_url"],
                "link": item["promotion_link"],
                "discount": discount,
            })
    except Exception as e:
        print(f"Parse error: {e}")
    return products

def format_message(product, is_auto=False):
    urgency = get_urgency()
    msg = (
        f"🛍️ <b>{product['name']}</b>\n\n"
        f"💰 מחיר מיוחד: <b>{product['price']}</b>\n"
        f"🔥 חיסכון של: <b>{product['discount']}% הנחה!</b>\n\n"
        f"{urgency}\n\n"
        f"👉 <a href='{product['link']}'>לחץ כאן לקנייה עם משלוח חינם!</a>"
    )
    return msg

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
                text = text.replace("@Isradeals_il_bot", "").strip()
                if text:
                    min_p, max_p = parse_price_range(text)
                    send_telegram(f"🔍 מחפש עבורך את הדיל הכי טוב על <b>{text}</b>...", chat_id=chat_id)
                    keyword_en = translate_to_english(text)
                    products = get_products(keyword_en, min_p, max_p)
                    if products:
                        send_telegram(f"✅ מצאתי <b>{len(products[:5])}</b> מוצרים מעולים!", chat_id=chat_id)
                        for p in products[:5]:
                            send_telegram(format_message(p), p["img"], chat_id=chat_id)
                            time.sleep(2)
                    else:
                        send_telegram("😔 לא נמצאו מוצרים מתאימים כרגע.\nנסה מילת חיפוש אחרת או טווח מחיר שונה.", chat_id=chat_id)
        except Exception as e:
            print(f"Handle error: {e}")
    return offset

print("Starting...")
send_telegram(
    "🎉 <b>ברוכים הבאים ל-AliDeals Israel!</b>\n\n"
    "אני מוצא לך את הדילים הכי טובים מאלי אקספרס 🛍️\n\n"
    "🔍 <b>איך לחפש?</b>\n"
    "פשוט שלח לי מה אתה מחפש:\n"
    "• שרשרת זהב\n"
    "• נעלי בית לגבר\n"
    "• תיק עור 50-200 שח\n"
    "• כובע צמר שחור\n\n"
    "⚡ אני אמצא לך את המחיר הכי זול עם הנחה מעל 20%!"
)
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
            print(f"Auto: {kw}")
            products = get_products(kw)
            for p in products:
                if p["link"] not in sent:
                    send_telegram(format_message(p, is_auto=True), p["img"])
                    sent.add(p["link"])
                    time.sleep(5)
            ki += 1
            last_auto = time.time()
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(10)
