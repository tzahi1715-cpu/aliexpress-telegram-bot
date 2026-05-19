import requests
import time
import hashlib
import re
import random
import json
import os

TELEGRAM_TOKEN = "7419793459:AAE0mSRGuNituAJDZ5wdmplG5F8VsLpZGHQ"
CHAT_ID = "-5136013039"
APP_KEY = "534108"
APP_SECRET = "2nSUuI2T0IfFwvNb1TpAmpeILtsjCszH"
USD_TO_ILS = 3.7
MIN_PRICE_ILS = 10
SENT_FILE = "sent_products.json"
MAX_SENT = 1000

URGENCY_PHRASES = [
    "⏰ מלאי מוגבל - הזדרזי!",
    "🔥 נמכר בקצב מטורף!",
    "⚡ הצעה לזמן מוגבל!",
    "🏃 אל תפספסי את המחיר הזה!",
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

REQUIRED_WORDS = {
    "necklace": ["necklace", "chain", "pendant", "choker"],
    "bracelet": ["bracelet", "bangle", "cuff"],
    "earring": ["earring", "ear stud", "ear hoop"],
    "ring": ["ring"],
    "bag": ["bag", "handbag", "purse", "tote", "backpack"],
    "wallet": ["wallet", "card holder"],
    "shoes": ["shoes", "sneaker", "boot", "heel", "slipper", "sandal"],
    "slipper": ["slipper", "mule", "slide"],
    "hat": ["hat", "cap", "beanie", "beret"],
    "watch": ["watch"],
    "shirt": ["shirt", "blouse", "top", "tee"],
    "dress": ["dress", "skirt", "gown"],
    "coat": ["coat", "jacket", "hoodie", "sweater"],
}

def load_sent():
    try:
        if os.path.exists(SENT_FILE):
            with open(SENT_FILE, "r") as f:
                return set(json.load(f))
    except:
        pass
    return set()

def save_sent(sent):
    try:
        sent_list = list(sent)
        if len(sent_list) > MAX_SENT:
            sent_list = sent_list[-MAX_SENT:]
        with open(SENT_FILE, "w") as f:
            json.dump(sent_list, f)
    except:
        pass

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

def shorten_url(url):
    try:
        r = requests.get(f"https://tinyurl.com/api-create.php?url={url}", timeout=10)
        if r.status_code == 200:
            return r.text.strip()
    except:
        pass
    return url

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

def get_products(keyword, min_price=None, max_price=None, page=1):
    ts = str(int(time.time() * 1000))
    params = {
        "app_key": APP_KEY,
        "timestamp": ts,
        "sign_method": "md5",
        "method": "ali
