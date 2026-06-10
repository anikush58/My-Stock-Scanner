from fastapi import FastAPI

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

