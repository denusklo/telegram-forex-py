# auth_telegram.py
import asyncio
from telethon import TelegramClient
import os
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE_NUMBER = os.getenv('TELEGRAM_PHONE_NUMBER')

async def main():
    client = TelegramClient('session', API_ID, API_HASH)
    await client.start(phone=PHONE_NUMBER)
    print("Authentication successful. Session file created.")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())