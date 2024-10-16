from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.db.database import Base
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)
    pair = Column(String)
    price = Column(Float)
    sl = Column(Float)  # Stop Loss
    tp = Column(Float)  # Take Profit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Pydantic models for API interactions
class TradingSignal(BaseModel):
    action: str
    pair: str
    price: float
    sl: float
    tp: float

class TradeResponse(BaseModel):
    id: int
    action: str
    pair: str
    price: float
    sl: float
    tp: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)