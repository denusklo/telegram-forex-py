from app.models.trade import TradingSignal

def parse_message(message: str) -> TradingSignal:
    # Your parsing logic here
    pass

async def execute_trade(signal: TradingSignal):
    # Your trade execution logic here
    pass
