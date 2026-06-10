from pydantic import BaseModel

class StockCreate(BaseModel):
    symbol: str
    exchange: str

