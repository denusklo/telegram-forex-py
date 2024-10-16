from contextlib import asynccontextmanager
import os
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from telethon import TelegramClient, events
import asyncio
from dotenv import load_dotenv
from typing import Optional, List, Dict
import queue
from datetime import datetime
import aiofiles
import re
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_db
from app.models.channel import Channel, ChannelCreate, ChannelResponse

load_dotenv()

# Telegram configuration
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE_NUMBER = os.getenv('TELEGRAM_PHONE_NUMBER')

# Log file configuration
LOG_FILE = "bot_logs.txt"

client = TelegramClient('session', API_ID, API_HASH)
client_ready = asyncio.Event()
background_tasks: Dict[int, asyncio.Task] = {}
log_queue = asyncio.Queue()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await client.start()
    client_ready.set()
    yield
    # Shutdown
    for task in background_tasks.values():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    await client.disconnect()

app = FastAPI(lifespan=lifespan)

async def log_message(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    print(log_entry.strip())
    await log_queue.put(log_entry)
    
    async with aiofiles.open(LOG_FILE, mode='a') as f:
        await f.write(log_entry)

async def listen_to_channel(channel_id: int):
    await client_ready.wait()
    try:
        await log_message(f"Starting to listen to channel with ID: {channel_id}")
        
        @client.on(events.NewMessage(chats=channel_id))
        async def handler(event):
            message = event.message.text
            await log_message(f"New message received from channel {channel_id}: {message}")
            trading_signal = parse_message(message)
            await log_message(f"Parsed signal from channel {channel_id}: {trading_signal}")

        await client.run_until_disconnected()
    except asyncio.CancelledError:
        await log_message(f"Listening task for channel {channel_id} was cancelled.")
    except Exception as e:
        await log_message(f"Error in listen_to_channel for channel {channel_id}: {e}")
    finally:
        await log_message(f"Stopped listening to channel {channel_id}.")

def parse_message(message: str) -> Optional[Dict[str, str]]:
    # Your existing parse_message function here
    pass

@app.post("/channels/", response_model=ChannelResponse)
async def create_channel(channel: ChannelCreate, db: AsyncSession = Depends(get_db)):
    db_channel = Channel(channel_id=channel.channel_id, name=channel.name)
    db.add(db_channel)
    await db.commit()
    await db.refresh(db_channel)
    
    # Start listening to the new channel
    channel_id = int(channel.channel_id)
    if channel_id not in background_tasks:
        background_tasks[channel_id] = asyncio.create_task(listen_to_channel(channel_id))
    
    return db_channel

@app.get("/channels/", response_model=list[ChannelResponse])
async def read_channels(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Channel).offset(skip).limit(limit))
    channels = result.scalars().all()
    return channels

@app.get("/channels/{channel_id}", response_model=ChannelResponse)
async def read_channel(channel_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Channel).filter(Channel.id == channel_id))
    db_channel = result.scalars().first()
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return db_channel

@app.delete("/channels/{channel_id}", response_model=ChannelResponse)
async def delete_channel(channel_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Channel).filter(Channel.id == channel_id))
    db_channel = result.scalars().first()
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Stop listening to the channel
    channel_id_int = int(db_channel.channel_id)
    if channel_id_int in background_tasks:
        background_tasks[channel_id_int].cancel()
        try:
            await background_tasks[channel_id_int]
        except asyncio.CancelledError:
            pass
        del background_tasks[channel_id_int]
    
    await db.delete(db_channel)
    await db.commit()
    return db_channel

@app.post("/start")
async def start_bot(db: AsyncSession = Depends(get_db)):
    if not client_ready.is_set():
        await client_ready.wait()
    if not client.is_connected():
        await client.connect()
    
    result = await db.execute(select(Channel))
    channels = result.scalars().all()
    for channel in channels:
        channel_id = int(channel.channel_id)
        if channel_id not in background_tasks:
            background_tasks[channel_id] = asyncio.create_task(listen_to_channel(channel_id))
    
    return {"message": "Bot started listening to all channels"}

@app.post("/stop")
async def stop_bot():
    for task in background_tasks.values():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    background_tasks.clear()
    return {"message": "Bot stopped listening to all channels"}

@app.get("/")
async def root():
    return {"message": "Telegram Forex Bot is running"}

@app.get("/logs")
async def get_logs():
    logs = []
    while not log_queue.empty():
        logs.append(await log_queue.get())
    return {"logs": logs}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)