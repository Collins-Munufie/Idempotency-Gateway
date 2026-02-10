from fastapi import FastAPI
from app.store import IdempotencyStore

app = FastAPI(title="Idempotency Gateway")

store = IdempotencyStore()

@app.get("/health")
def health_check():
    return {"status": "ok"}
