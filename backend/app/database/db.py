from sqlalchemy import create_engine

DATABASE_URL = "postgresql://stockuser:K16101996k@postgres:5432/stockscanner"

engine = create_engine(DATABASE_URL)



