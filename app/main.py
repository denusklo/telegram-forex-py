from fastapi import FastAPI
from app.core.config import Settings
from app.api.endpoints import bot, trades
from app.db.database import init_db

settings = Settings()

app = FastAPI()

app.include_router(bot.router)
app.include_router(trades.router)

@app.on_event("startup")
async def startup_event():
    await init_db()

# app/services/telegram_bot.py
from telethon import TelegramClient, events
from app.core.config import settings
from app.services.trading import parse_message, execute_trade

client = TelegramClient('session', settings.API_ID, settings.API_HASH)

async def start_listening():
    await client.start(phone=settings.PHONE_NUMBER)
    
    @client.on(events.NewMessage(chats=settings.CHANNEL_IDS))
    async def handler(event):
        message = event.message.text
        trading_signal = parse_message(message)
        if trading_signal:
            await execute_trade(trading_signal)

    await client.run_until_disconnected()