from fastapi import FastAPI
from sqlalchemy import text

from app.database.db import engine
from app.schemas.stock import StockCreate

app = FastAPI(
    title="My Stock Scanner",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "status": "running",
        "app": "my-stock-scanner"
    }

@app.get("/health")
def health():
    return {
        "healthy": True
    }

@app.get("/stocks")
def get_stocks():
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT id, symbol, exchange
                FROM stocks
                ORDER BY symbol
                """
            )
        )

        rows = [
            {
                "id": row.id,
                "symbol": row.symbol,
                "exchange": row.exchange
            }
            for row in result
        ]

        return rows

@app.post("/stocks")
def create_stock(stock: StockCreate):
    with engine.connect() as conn:
        conn.execute(
            text(
                """
                INSERT INTO stocks(symbol, exchange)
                VALUES (:symbol, :exchange)
                """
            ),
            {
                "symbol": stock.symbol.upper(),
                "exchange": stock.exchange.upper()
            }
        )

        conn.commit()

    return {
        "message": "Stock added",
        "symbol": stock.symbol.upper()
    }

@app.delete("/stocks/{stock_id}")
def delete_stock(stock_id: int):
    with engine.connect() as conn:
        conn.execute(
            text(
                """
                DELETE FROM stocks
                WHERE id = :id
                """
            ),
            {"id": stock_id}
        )

        conn.commit()

    return {
        "message": "Stock deleted",
        "id": stock_id
    }

