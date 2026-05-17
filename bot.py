import requests
import time
import hashlib
import re
import random

TELEGRAM_TOKEN = "7419793459:AAE0mSRGuNituAJDZ5wdmplG5F8VsLpZGHQ"
CHAT_ID = "-5136013039"
APP_KEY = "534108"
APP_SECRET = "2nSUuI2T0IfFwvNb1TpAmpeILtsjCszH"
USD_TO_ILS = 3.7

URGENCY_PHRASES = [
    "⏰ מלאי מוגבל - הזדרז!",
    "🔥 נמכר בקצב מטורף!",
    "⚡ הצעה לזמן מוגבל!",
    "🏃 אל תפספס את המחיר הזה!",
    "💎 עסקה שאי אפשר לסרב לה!",
]

GENDER_MAP = {
    "לגבר": "men", "לגברים": "men", "גברי": "men", "גברים": "men",
    "לאישה": "women", "לנשים": "women", "נשי": "women", "נשים": "women",
    "לילד": "kids boy", "לילדה": "kids girl", "לילדים": "kids",
    "לתינוק": "baby", "לתינוקת": "baby girl",
}

COLOR_MAP = {
    "זהב": "gold", "זהבי": "gold",
    "כסף": "silver", "כסוף": "silver",
    "שחור": "black", "שחורה": "black",
    "לבן": "white", "לבנה": "white",
    "אדום": "red", "אדומה": "red",
    "כחול": "blue", "כחולה": "blue",
    "ירוק": "green", "ירוקה": "green",
    "ורוד": "pink", "ורודה": "pink",
    "סגול": "purple", "סגולה": "purple",
    "חום": "brown", "חומה": "brown",
    "אפור": "gray", "אפורה": "gray",
    "צהוב": "yellow", "צהובה": "yellow",
    "כתום": "orange", "כתומה": "orange",
    "בז": "beige",
}

# מילות מפתח חייבות להופיע בכותרת
REQUIRED_WORDS = {
    "necklace": ["necklace", "chain", "pendant", "choker"],
    "bracelet": ["bracelet", "bangle", "cuff"],
    "earring": ["earring", "ear", "stud", "hoop"],
    "ring": ["ring"],
    "bag": ["bag", "handbag", "purse", "tote", "backpack"],
    "wallet": ["wallet", "purse", "card holder"],
    "shoes": ["shoes", "sneaker", "boot", "heel", "slipper", "sandal"],
    "slipper": ["slipper", "mule", "slide"],
    "hat": ["hat", "cap", "beanie", "beret"],
    "watch": ["watch", "timepiece"],
    "shirt": ["shirt", "blouse", "top", "tee"],
    "dress": ["dress", "skirt", "gown"],
    "coat": ["coat", "jacket", "hoodie", "sweater"],
}

def get_required_words(keyword):
    keyword_lower = keyword.lower()
    for key, words in REQUIRED_WORDS.items():
        if key in keyword_lower:
            return words
    return keyword_lower.split()[:2]

def is_relevant(title, keyword):
    title_lower = title.lower()
    required = get_required_words(keyword)
    return any(word in title_lower for word in required)

def translate_to_english(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "he", "tl": "en", "dt": "t", "q": text[:200]}
        r = requests.get(url, params=params, timeout=10)
        result = r.json()[0][0][0]
    except:
        result = text
    for he_word, en_word in GENDER_MAP.items():
        if he_word in text and en_word not in result.lower():
            result = en_word + " " + result
            break
    for he_color, en_color in COLOR_MAP.items():
        if he_color in text and en_color not in result.lower():
            result = result + " " + en_color
            break
    result = re.sub(r'[א-ת]+', '', result).strip()
    print(f"Translated: {text} -> {result}")
    return result

def translate_to_hebrew(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "en", "tl": "he", "dt": "t", "q": text[:200]}
        r = requests.get(url, params=params, timeout=10)
        return r.json()[0][0][0]
    except:
        return text

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

def safe_int(val):
    try:
        return int(float(str(val).strip() or 0))
    except:
        return 0

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
        "sort": "SALE_PRICE_ASC",
        "ship_to_country": "IL",
        "free_shiping": "y",
    }
    params["sign"] = sign(params)
    r = requests.post("https://api-sg.aliexpress.com/sync", data=params, timeout=20)
    products = []
    try:
        data = r.json()
        items = data["aliexpress_affiliate_product_query_response"]["resp_result"]["result"]["products"]["product"]
        for item in items:
            try:
                title = item.get("product_title", "")

                # בדיקת רלוונטיות חזקה
                if not is_relevant(title, keyword):
                    print(f"Skipped (not relevant): {title[:50]}")
                    continue

                price_usd = float(item["target_sale_price"])
                price_ils = round(price_usd * USD_TO_ILS, 2)

                if min_price and price_ils < min_price:
                    continue
                if max_price and price_ils > max_price:
                    continue

                name_he = translate_to_hebrew(title)
                discount = safe_int(item.get("discount", 0))

                products.append({
                    "name": name_he,
                    "price": f"₪{price_ils}",
                    "img": item["product_main_image_url"],
                    "link": item["promotion_link"],
                    "discount": discount,
                })
            except Exception as e:
                print(f"Item error: {e}")
                continue
    except Exception as e:
        print(f"Parse error: {e}")
    return products

def format_message(product):
    urgency = random.choice(URGENCY_PHRASES)
    discount_text = f"🔥 הנחה של <b>{product['discount']}%!</b>\n" if product['discount'] > 0 else ""
    msg = (
        f"🛍️ <b>{product['name']}</b>\n\n"
        f"💰 מחיר: <b>{product['price']}</b>\n"
        f"🚚 משלוח חינם! 🎁\n"
        f"{discount_text}"
        f"{urgency}\n\n"
        f"👉 <a href='{product['link']}'>לחץ כאן לקנייה!</a>"
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
                    send_telegram(f"🔍 מחפש עבורך <b>{text}</b> עם משלוח חינם...", chat_id=chat_id)
                    keyword_en = translate_to_english(text)
                    products = get_products(keyword_en, min_p, max_p)
                    if products:
                        send_telegram(f"✅ מצאתי <b>{len(products[:5])}</b> מוצרים!", chat_id=chat_id)
                        for p in products[:5]:
                            send_telegram(format_message(p), p["img"], chat_id=chat_id)
                            time.sleep(2)
                    else:
                        send_telegram("😔 לא נמצאו מוצרים מתאימים.\nנסה מילת חיפוש אחרת.", chat_id=chat_id)
        except Exception as e:
            print(f"Handle error: {e}")
    return offset

print("Starting...")
send_telegram(
    "🎉 <b>ברוכים הבאים ל-AliDeals Israel!</b>\n\n"
    "אני מוצא לך דילים מאלי אקספרס עם <b>משלוח חינם בלבד!</b> 🚚🎁\n\n"
    "🔍 <b>איך לחפש?</b>\n"
    "• שרשרת זהב\n"
    "• נעלי בית לגברים\n"
    "• תיק עור 50-200 שח\n"
    "• כובע צמר שחור לגבר\n\n"
    "⚡ אני אמצא לך את המחיר הכי זול!"
)
time.sleep(2)

keywords = [
    "gold necklace women", "silver bracelet women",
    "pearl earrings women", "ring women jewelry",
    "hair accessories women", "crystal necklace",
    "charm bracelet", "vintage earrings",
    "women handbag", "crossbody bag women",
    "tote bag women", "backpack women",
    "wallet women leather",
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
                    send_telegram(format_message(p), p["img"])
                    sent.add(p["link"])
                    time.sleep(5)
            ki += 1
            last_auto = time.time()
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(10)
