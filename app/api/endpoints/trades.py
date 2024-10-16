from fastapi import APIRouter
from app.models.trade import TradingSignal
from app.services.trading import execute_trade

router = APIRouter()

@router.post("/manual_trade")
async def manual_trade(signal: TradingSignal):
    await execute_trade(signal)
    return {"message": "Trade executed successfully"}

