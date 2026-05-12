import asyncio
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

# הגדרות
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ALI_APP_KEY = os.getenv("ALIEXPRESS_APP_KEY")  # 534108
ALI_APP_SECRET = os.getenv("ALIEXPRESS_APP_SECRET")
CHAT_ID = os.getenv("CHAT_ID", "-5136013039")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "🚀 **ברוך הבא לבוט דילים של AliExpress!**\n\n"
        "שלח /deals כדי לקבל דילים חמים\n"
        "שלח לינק של מוצר ואני אהפוך אותו לקישור עם עמלה"
    )

@dp.message(Command("deals"))
async def send_deals(message: Message):
    await message.answer("🔍 מחפש דילים חמים מאלי אקספרס...")

    # דוגמה ראשונית - נשתמש ב-AliExpress API מאוחר יותר
    await message.answer(
        "📌 **דילים לדוגמה:**\n"
        "🛍 אוזניות Bluetooth - 55% הנחה\n"
        "🔗 [לקנייה](https://s.click.aliexpress.com/e/_DdKL9lz)\n\n"
        "יותר דילים אמיתיים בקרוב!"
    )

# הפעלה
async def main():
    print("✅ הבוט רץ...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
