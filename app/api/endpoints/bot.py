from fastapi import APIRouter
from app.services.telegram_bot import start_listening, client

router = APIRouter()

@router.post("/start")
async def start_bot():
    if not client.is_connected():
        await start_listening()
    return {"message": "Bot started listening to Telegram channels"}

@router.post("/stop")
async def stop_bot():
    if client.is_connected():
        await client.disconnect()
    return {"message": "Bot stopped listening to Telegram channels"}

