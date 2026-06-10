from fastapi import FastAPI
from sqlalchemy import text

from app.database.db import engine

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

