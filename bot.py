import requests
import time

TELEGRAM_TOKEN = "7419793459:AAGhSAzyDmg-7GFJrww0UXwYy2ia7N9m2jI"
CHAT_ID = "-5136013039"

PRODUCTS = [
    {
        "name": "אוזניות Bluetooth אלחוטיות TWS",
        "price": "$8.99",
        "discount": "55%",
        "img": "https://ae01.alicdn.com/kf/S8c2cd3e5c7964d0a94f0d55d2f59e8b8r.jpg",
        "link": "https://s.click.aliexpress.com/e/_DdKL9lz"
    },
    {
        "name": "שעון חכם Smart Watch Sport",
        "price": "$15.99",
        "discount": "40%",
        "img": "https://ae01.alicdn.com/kf/HTB1YNybXlCw3KVjSZFlq6AJkFXal.jpg",
        "link": "https://s.click.aliexpress.com/e/_DlbXvlz"
    },
    {
        "name": "מטען נייד 20000mAh מהיר",
        "price": "$12.99",
        "discount": "35%",
        "img": "https://ae01.alicdn.com/kf/HTB1f7Y9XoD1gK0jSZFsq6zldVXah.jpg",
        "link": "https://s.click.aliexpress.com/e/_DCmBvlz"
    },
    {
        "name": "רצועת LED RGB חכמה 5M",
        "price": "$6.99",
        "discount": "60%",
        "img": "https://ae01.alicdn.com/kf/HTB1Z8nGaRv0gK0jSZKbq6zK2FXaJ.jpg",
        "link": "https://s.click.aliexpress.com/e/_DeBBvlz"
    },
    {
        "name": "מצלמת אבטחה WiFi 1080P",
        "price": "$18.99",
        "discount": "45%",
        "img": "https://ae01.alicdn.com/kf/HTB1X8Y6XoD1gK0jSZFsq6zldVXan.jpg",
        "link": "https://s.click.aliexpress.com/e/_DFcBvlz"
    },
    {
        "name": "כבל USB-C מהיר 100W",
        "price": "$3.99",
        "discount": "50%",
        "img": "https://ae01.alicdn.com/kf/HTB1nK8LaIfrK1RjSspbq6A6JFXaY.jpg",
        "link": "https://s.click.aliexpress.com/e/_DGhBvlz"
    },
    {
        "name": "מעמד טלפון לרכב מגנטי",
        "price": "$4.99",
        "discount": "65%",
        "img": "https://ae01.alicdn.com/kf/HTB1Y8nGaIfrK1RjSspbq6A6JFXaP.jpg",
        "link": "https://s.click.aliexpress.com/e/_DHiBvlz"
    },
]

def send_telegram(text, image_url=None):
    try:
        if image_url:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            data = {
                "chat_id": CHAT_ID,
                "photo": image_url,
                "caption": text,
                "parse_mode": "HTML"
            }
        else:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            data = {
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "HTML"
            }
        r = requests.post(url, data=data)
        print("Sent:", r.status_code)
    except Exception as e:
        print(f"Error: {e}")

send_telegram("🤖 הבוט התחיל לעבוד! מפרסם דילים מאלי אקספרס 🛍")
time.sleep(2)

i = 0
while True:
    try:
        p = PRODUCTS[i % len(PRODUCTS)]
        msg = (
            f"🛍 <b>{p['name']}</b>\n"
            f"💰 מחיר: <b>{p['price']}</b>\n"
            f"🔥 הנחה: <b>{p['discount']}</b>\n"
            f"🔗 <a href='{p['link']}'>לקנייה באלי אקספרס</a>"
        )
        send_telegram(msg, p['img'])
        i += 1
        time.sleep(3600)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)
