import requests
import time
import json
from iop import IopClient, IopRequest

# =========================
# CONFIG
# =========================

TELEGRAM_TOKEN = "7419793459:AAHqTSUlW_eg55ugxfe5-l_FYRcqSh-2nIw"
CHANNEL_USERNAME = "@AliDealsIsrael"

APP_KEY = "534108"
APP_SECRET = "ilaCwDuzjSfpMqWjnh0UUSd4QfiHPchT"

TRACKING_ID = "default"

# =========================
# TELEGRAM SEND FUNCTION
# =========================

def send_telegram(text, image_url=None):

    try:

        if image_url:

            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"

            data = {
                "chat_id": CHANNEL_USERNAME,
                "photo": image_url,
                "caption": text,
                "parse_mode": "HTML"
            }

        else:

            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

            data = {
                "chat_id": CHANNEL_USERNAME,
                "text": text,
                "parse_mode": "HTML"
            }

        r = requests.post(url, data=data)

        print("Telegram Status:", r.status_code)
        print(r.text)

    except Exception as e:
        print("Telegram Error:", e)

# =========================
# GET PRODUCTS
# =========================

def get_products():

    products = []

    try:

        client = IopClient(
            "https://api-sg.aliexpress.com/sync",
            APP_KEY,
            APP_SECRET
        )

        request = IopRequest(
            "aliexpress.affiliate.hotproduct.query"
        )

        request.add_api_param("page_size", "10")
        request.add_api_param("target_currency", "USD")
        request.add_api_param("target_language", "EN")
        request.add_api_param("tracking_id", TRACKING_ID)

        response = client.execute(request)

        data = json.loads(response.body)

        result = data.get(
            "aliexpress_affiliate_hotproduct_query_response",
            {}
        )

        resp_result = result.get("resp_result", {})
        result_data = resp_result.get("result", {})
        products_data = result_data.get("products", {})
        items = products_data.get("product", [])

        for item in items:

            title = item.get("product_title", "AliExpress Product")
            price = item.get("target_sale_price", "0")
            image = item.get("product_main_image_url", "")
            link = item.get("promotion_link", "")

            products.append({
                "title": title,
                "price": price,
                "image": image,
                "link": link
            })

    except Exception as e:
        print("AliExpress Error:", e)

    return products

# =========================
# MAIN LOOP
# =========================

print("BOT STARTED")

send_telegram("🤖 Bot Started Successfully")

sent_links = set()

while True:

    try:

        products = get_products()

        print(f"Found {len(products)} products")

        for product in products:

            if product["link"] not in sent_links:

                message = f"""
🔥 <b>{product['title'][:100]}</b>

💰 Price: <b>${product['price']}</b>

🛒 <a href="{product['link']}">Buy Now</a>
"""

                send_telegram(
                    message,
                    product["image"]
                )

                sent_links.add(product["link"])

                print("Product Sent")

                time.sleep(10)

    except Exception as e:
        print("MAIN LOOP ERROR:", e)

    print("Waiting 1 hour...")

    time.sleep(3600)
