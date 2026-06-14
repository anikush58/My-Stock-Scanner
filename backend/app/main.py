from fastapi import FastAPI, HTTPException
from sqlalchemy import text

from app.database.db import engine
from app.schemas.stock import StockCreate
from app.services.upstox import (
    get_profile,
    get_candles,
    search_instrument,
    scan_stock
)

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

@app.get("/watchlists")
def get_watchlists():

    with engine.connect() as conn:

        rows = conn.execute(
            text("""
                SELECT
                    id,
                    name
                FROM watchlists
                ORDER BY name
            """)
        ).fetchall()

    return [
        {
            "id": row.id,
            "name": row.name
        }
        for row in rows
    ]


@app.get("/watchlists/{name}")
def get_watchlist(name: str):

    with engine.connect() as conn:

        rows = conn.execute(
            text("""
                SELECT
                    s.symbol,
                    s.instrument_key
                FROM watchlist_stocks ws
                JOIN watchlists w
                    ON ws.watchlist_id = w.id
                JOIN stocks s
                    ON ws.stock_id = s.id
                WHERE UPPER(w.name) = UPPER(:name)
                ORDER BY s.symbol
            """),
            {"name": name}
        ).fetchall()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Watchlist not found"
        )

    return [
        {
            "symbol": row.symbol,
            "instrument_key": row.instrument_key
        }
        for row in rows
    ]


@app.get("/watchlists/{name}/scanner")
def scan_watchlist(name: str):

    with engine.connect() as conn:

        rows = conn.execute(
            text("""
                SELECT
                    s.symbol,
                    s.instrument_key
                FROM watchlist_stocks ws
                JOIN watchlists w
                    ON ws.watchlist_id = w.id
                JOIN stocks s
                    ON ws.stock_id = s.id
                WHERE
                    UPPER(w.name) = UPPER(:name)
                    AND s.active = TRUE
                ORDER BY s.symbol
            """),
            {"name": name}
        ).fetchall()

    results = []

    for stock in rows:

        if not stock.instrument_key:
            continue

        try:

            results.append(
                scan_stock(
                    stock.symbol,
                    stock.instrument_key
                )
            )

        except Exception as e:

            results.append(
                {
                    "symbol": stock.symbol,
                    "error": str(e)
                }
            )

    return results

@app.post("/watchlists")
def create_watchlist(name: str):

    with engine.connect() as conn:

        conn.execute(
            text("""
                INSERT INTO watchlists(name)
                VALUES (:name)
            """),
            {"name": name.upper()}
        )

        conn.commit()

    return {
        "message": "Watchlist created",
        "name": name.upper()
    }


@app.post("/watchlists/{name}/add/{symbol}")
def add_stock_to_watchlist(name: str, symbol: str):

    with engine.connect() as conn:

        watchlist = conn.execute(
            text("""
                SELECT id
                FROM watchlists
                WHERE UPPER(name)=UPPER(:name)
            """),
            {"name": name}
        ).fetchone()

        if not watchlist:
            raise HTTPException(
                status_code=404,
                detail="Watchlist not found"
            )

        stock = conn.execute(
            text("""
                SELECT id
                FROM stocks
                WHERE UPPER(symbol)=UPPER(:symbol)
            """),
            {"symbol": symbol}
        ).fetchone()

        if not stock:
            raise HTTPException(
                status_code=404,
                detail="Stock not found"
            )

        conn.execute(
            text("""
                INSERT INTO watchlist_stocks
                (
                    watchlist_id,
                    stock_id
                )
                VALUES
                (
                    :watchlist_id,
                    :stock_id
                )
                ON CONFLICT DO NOTHING
            """),
            {
                "watchlist_id": watchlist.id,
                "stock_id": stock.id
            }
        )

        conn.commit()

    return {
        "message": "Stock added",
        "watchlist": name.upper(),
        "symbol": symbol.upper()
    }


@app.delete("/watchlists/{name}/{symbol}")
def remove_stock_from_watchlist(
    name: str,
    symbol: str
):

    with engine.connect() as conn:

        conn.execute(
            text("""
                DELETE FROM watchlist_stocks
                WHERE watchlist_id IN (
                    SELECT id
                    FROM watchlists
                    WHERE UPPER(name)=UPPER(:name)
                )
                AND stock_id IN (
                    SELECT id
                    FROM stocks
                    WHERE UPPER(symbol)=UPPER(:symbol)
                )
            """),
            {
                "name": name,
                "symbol": symbol
            }
        )

        conn.commit()

    return {
        "message": "Stock removed",
        "watchlist": name.upper(),
        "symbol": symbol.upper()
    }


@app.get("/upstox/profile")
def upstox_profile():
    return get_profile()

@app.get("/candles/{symbol}")
def candles(symbol: str):
    return get_candles(symbol)

@app.get("/search/{symbol}")
def search(symbol: str):
    return search_instrument(symbol)

@app.get("/scanner")
def scanner():

    with engine.connect() as conn:

        stocks = conn.execute(
            text("""
                SELECT
                    symbol,
                    instrument_key
                FROM stocks
                WHERE active = TRUE
                ORDER BY symbol
            """)
        ).fetchall()

    results = []

    for stock in stocks:

        if not stock.instrument_key:
            continue

        try:

            results.append(
                scan_stock(
                    stock.symbol,
                    stock.instrument_key
                )
            )

        except Exception as e:

            results.append(
                {
                    "symbol": stock.symbol,
                    "error": str(e)
                }
            )

    return results

@app.get("/watchlists/{name}/leaderboard")
def watchlist_leaderboard(name: str):

    with engine.connect() as conn:

        stocks = conn.execute(
            text("""
                SELECT
                    s.symbol,
                    s.instrument_key
                FROM watchlist_stocks ws
                JOIN watchlists w
                    ON ws.watchlist_id = w.id
                JOIN stocks s
                    ON ws.stock_id = s.id
                WHERE
                    UPPER(w.name) = UPPER(:name)
                    AND s.active = TRUE
                ORDER BY s.symbol
            """),
            {"name": name}
        ).fetchall()

    results = []

    for stock in stocks:

        if not stock.instrument_key:
            continue

        try:

            result = scan_stock(
                stock.symbol,
                stock.instrument_key
            )

            results.append(result)

        except Exception:
            pass

    ranked = sorted(
        results,
        key=lambda x: x["momentum_score"],
        reverse=True
    )

    leaderboard_data = []

    for index, stock in enumerate(ranked, start=1):

        leaderboard_data.append(
            {
                "rank": index,
                "symbol": stock["symbol"],
                "momentum_score": stock["momentum_score"],
                "signal": stock["signal"]
            }
        )

    return leaderboard_data


@app.get("/leaderboard")
def leaderboard():

    with engine.connect() as conn:

        stocks = conn.execute(
            text("""
                SELECT
                    symbol,
                    instrument_key
                FROM stocks
                WHERE active = TRUE
                ORDER BY symbol
            """)
        ).fetchall()

    results = []

    for stock in stocks:

        if not stock.instrument_key:
            continue

        try:

            result = scan_stock(
                stock.symbol,
                stock.instrument_key
            )

            results.append(result)

        except Exception:
            pass

    ranked = sorted(
        results,
        key=lambda x: x["momentum_score"],
        reverse=True
    )

    leaderboard_data = []

    for index, stock in enumerate(ranked, start=1):

        leaderboard_data.append(
            {
                "rank": index,
                "symbol": stock["symbol"],
                "momentum_score": stock["momentum_score"],
                "signal": stock["signal"]
            }
        )

    return leaderboard_data




