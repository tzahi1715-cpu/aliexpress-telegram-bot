import requests
import time
import hashlib
import re
import html
import random

# =========================
# CONFIG
# =========================

TELEGRAM_TOKEN = "NEW_TELEGRAM_TOKEN"
CHAT_ID = "-100XXXXXXXXXX"

APP_KEY = "NEW_APP_KEY"
APP_SECRET = "NEW_APP_SECRET"

USD_TO_ILS = 3.1

MIN_PRICE_ILS = 20
MIN_RATING = 0
MIN_DISCOUNT = 0

AUTO_POST_EVERY = 3600
MAX_PRODUCTS_SEND = 5

translation_cache = {}
sent_products = set()
user_sent = {}

# =========================
# DICTIONARY
# =========================

DICTIONARY = {
    "כובע": "hat",
    "כובע צמר": "wool hat beanie",
    "כובע קש": "straw hat",
    "שרשרת": "necklace",
    "שרשרת זהב": "gold necklace",
    "שרשרת פנינים": "pearl necklace",
    "שרשרת כסף": "silver necklace",
    "טבעת": "ring",
    "טבעת זהב": "gold ring",
    "טבעת כסף": "silver ring",
    "עגיל": "earring",
    "עגילים": "earrings",
    "עגילי פנינים": "pearl earrings",
    "צמיד": "bracelet",
    "צמיד זהב": "gold bracelet",
    "צמיד כסף": "silver bracelet",
    "תיק": "handbag",
    "תיק עור": "leather handbag",
    "תיק יד": "handbag",
    "תיק גב": "backpack",
    "תיק צד": "crossbody bag",
    "ארנק": "wallet",
    "נעליים": "shoes",
    "נעלי עקב": "high heels",
    "כפכפים": "sandals",
    "נעלי ספורט": "sneakers",
    "נעלי בית": "slippers",
    "נעלי בית לגבר": "men slippers",
    "נעלי בית לאישה": "women slippers",
    "נעליים לגבר": "men shoes",
    "נעלי ספורט לגבר": "men sneakers",
    "שמלה": "dress",
    "חולצה": "shirt",
    "מעיל": "coat",
    "צעיף": "scarf",
    "כפפות": "gloves",
    "משקפי שמש": "sunglasses",
    "שעון": "watch",
    "שעון חכם": "smart watch",
    "שעון לגבר": "men watch",
    "שעון לאישה": "women watch",
    "אוזניות": "wireless earbuds",
    "טלפון": "phone case",
    "מטען": "power bank",
}

COLORS = {
    "זהב": "gold",
    "כסף": "silver",
    "שחור": "black",
    "לבן": "white",
    "אדום": "red",
    "כחול": "blue",
    "ירוק": "green",
    "ורוד": "pink",
    "סגול": "purple",
    "חום": "brown",
    "אפור": "gray",
    "צהוב": "yellow",
}

URGENCY_PHRASES = [
    "⏰ מלאי מוגבל - הזדרז!",
    "🔥 נמכר בקצב מטורף!",
    "⚡ הצעה לזמן מוגבל!",
    "🏃 אל תפספס את המחיר הזה!",
    "💎 עסקה שאי אפשר לסרב לה!",
]

# =========================
# HELPERS
# =========================

def get_urgency():
    return random.choice(URGENCY_PHRASES)

def translate_to_hebrew(text):

    if text in translation_cache:
        return translation_cache[text]

    try:
        url = "https://translate.googleapis.com/translate_a/single"

        params = {
            "client": "gtx",
            "sl": "en",
            "tl": "he",
            "dt": "t",
            "q": text[:200]
        }

        r = requests.get(url, params=params, timeout=10)

        result = r.json()[0][0][0]

        translation_cache[text] = result

        return result

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

        if text in translation_cache:
            return translation_cache[text]

        try:
            url = "https://translate.googleapis.com/translate_a/single"

            params = {
                "client": "gtx",
                "sl": "he",
                "tl": "en",
                "dt": "t",
                "q": text[:200]
            }

            r = requests.get(url, params=params, timeout=10)

            result = r.json()[0][0][0]

            translation_cache[text] = result

        except:
            result = text

    if "לגבר" in text and "men" not in result:
        result = "men " + result

    elif "לאישה" in text and "women" not in result:
        result = "women " + result

    for he_color, en_color in COLORS.items():
        if he_color in text and en_color not in result:
            result += f" {en_color}"
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

# =========================
# ALIEXPRESS
# =========================

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

    try:

        r = requests.post(
            "https://api-sg.aliexpress.com/sync",
            data=params,
            timeout=20
        )

        if r.status_code == 429:
            print("AliExpress Rate Limit")
            time.sleep(10)
            return []

        data = r.json()

        items = (
            data["aliexpress_affiliate_product_query_response"]
            ["resp_result"]
            ["result"]
            ["products"]
            ["product"]
        )

    except Exception as e:
        print(f"API ERROR: {e}")
        return []

    products = []

    for item in items:

        try:

            price_usd = float(item["target_sale_price"])
            price_ils = round(price_usd * USD_TO_ILS, 2)

            if price_ils < MIN_PRICE_ILS:
                continue

            if min_price and price_ils < min_price:
                continue

            if max_price and price_ils > max_price:
                continue

            try:
                rating = float(item.get("evaluate_rate", 0))

                if rating > 5:
                    rating = rating / 20

            except:
                rating = 0

            if rating > 0 and rating < MIN_RATING:
                continue

            discount_raw = str(item.get("discount", "0"))

            discount = int(
                re.sub(r"[^\d]", "", discount_raw) or 0
            )

            if discount < MIN_DISCOUNT:
                continue

            img = item.get("product_main_image_url")

            if not img:
                continue

            link = item.get("promotion_link")

            if not link:
                continue

            orders = item.get("lastest_volume", "0")

            original_price = item.get("target_original_price")

            name_he = translate_to_hebrew(
                item["product_title"]
            )

            products.append({
                "name": name_he,
                "price": price_ils,
                "original_price": original_price,
                "img": img,
                "link": link,
                "discount": discount,
                "rating": round(rating, 1),
                "orders": orders,
            })

        except Exception as e:
            print(f"PRODUCT ERROR: {e}")

    return products

# =========================
# TELEGRAM
# =========================

def format_message(product):

    urgency = get_urgency()

    safe_name = html.escape(product["name"])

    msg = (
        f"🛍️ <b>{safe_name}</b>\n\n"
        f"⭐ דירוג: <b>{product['rating']}/5</b>\n"
        f"📦 מעל <b>{product['orders']}</b> הזמנות\n"
        f"🚚 משלוח חינם לישראל\n\n"
        f"💸 במקום ₪{product['original_price']}\n"
        f"🔥 עכשיו רק <b>₪{product['price']}</b>\n"
        f"💥 {product['discount']}% הנחה\n\n"
        f"{urgency}"
    )

    return msg

def send_telegram(text, image_url=None, link=None, chat_id=None):

    cid = chat_id or CHAT_ID

    reply_markup = None

    if link:
        reply_markup = {
            "inline_keyboard": [[
                {
                    "text": "🛒 לקנייה עכשיו",
                    "url": link
                }
            ]]
        }

    try:

        if image_url:

            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"

            data = {
                "chat_id": cid,
                "photo": image_url,
                "caption": text,
                "parse_mode": "HTML"
            }

            if reply_markup:
                data["reply_markup"] = str(reply_markup).replace("'", '"')

        else:

            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

            data = {
                "chat_id": cid,
                "text": text,
                "parse_mode": "HTML"
            }

            if reply_markup:
                data["reply_markup"] = str(reply_markup).replace("'", '"')

        r = requests.post(url, data=data)

        print("Telegram:", r.status_code)

        if r.status_code == 429:
            print("Telegram Rate Limit")
            time.sleep(10)

    except Exception as e:
        print(f"TELEGRAM ERROR: {e}")

# =========================
# TELEGRAM UPDATES
# =========================

def get_updates(offset=None):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"

    params = {"timeout": 30}

    if offset:
        params["offset"] = offset

    try:

        r = requests.get(url, params=params, timeout=35)

        return r.json().get("result", [])

    except:
        return []

# =========================
# MESSAGE HANDLER
# =========================

def handle_messages(offset):

    updates = get_updates(offset)

    for update in updates:

        offset = update["update_id"] + 1

        try:

            msg = update.get("message", {})

            text = msg.get("text", "")

            chat_id = msg["chat"]["id"]

            if text and not text.startswith("/"):

                text = text.replace(
                    "@Isradeals_il_bot",
                    ""
                ).strip()

                if text:

                    min_p, max_p = parse_price_range(text)

                    send_telegram(
                        f"🔍 מחפש עבורך את הדיל הכי טוב על:\n\n<b>{html.escape(text)}</b>",
                        chat_id=chat_id
                    )

                    keyword_en = translate_to_english(text)

                    products = get_products(
                        keyword_en,
                        min_p,
                        max_p
                    )

                    if products:

                        sent_count = 0

                        for p in products:

                            if p["link"] in user_sent.get(chat_id, set()):
                                continue

                            send_telegram(
                                format_message(p),
                                p["img"],
                                p["link"],
                                chat_id
                            )

                            user_sent.setdefault(chat_id, set()).add(
                                p["link"]
                            )

                            sent_count += 1

                            time.sleep(2)

                            if sent_count >= MAX_PRODUCTS_SEND:
                                break

                    else:

                        send_telegram(
                            "😔 לא נמצאו מוצרים מתאימים כרגע.\nנסה חיפוש אחר.",
                            chat_id=chat_id
                        )

        except Exception as e:
            print(f"HANDLE ERROR: {e}")

    return offset

# =========================
# START MESSAGE
# =========================

send_telegram(
    "🎉 <b>ברוכים הבאים ל-AliDeals Israel</b>\n\n"
    "🛍️ אני מוצא לך את הדילים הכי טובים מאלי אקספרס\n\n"
    "🔍 פשוט שלח:\n"
    "• שרשרת זהב\n"
    "• נעלי בית לגבר\n"
    "• תיק עור 50-200 שח\n"
    "• כובע צמר שחור\n\n"
    "⚡ ותקבל מוצרים עם הנחות אמיתיות!"
)

# =========================
# AUTO KEYWORDS
# =========================

keywords = [
    "gold necklace women",
    "silver bracelet",
    "pearl earrings",
    "women handbag",
    "crossbody bag",
    "wireless earbuds",
    "smart watch",
    "women sneakers",
]

ki = 0
offset = None
last_auto = time.time()

print("BOT STARTED")

# =========================
# MAIN LOOP
# =========================

while True:

    try:

        offset = handle_messages(offset)

        if time.time() - last_auto >= AUTO_POST_EVERY:

            kw = keywords[ki % len(keywords)]

            print(f"AUTO SEARCH: {kw}")

            products = get_products(kw)

            for p in products:

                if p["link"] in sent_products:
                    continue

                send_telegram(
                    format_message(p),
                    p["img"],
                    p["link"]
                )

                sent_products.add(p["link"])

                time.sleep(5)

            ki += 1

            last_auto = time.time()

        time.sleep(1)

    except KeyboardInterrupt:
        print("STOPPED")
        break

    except Exception as e:

        print(f"MAIN LOOP ERROR: {e}")

        time.sleep(15)
