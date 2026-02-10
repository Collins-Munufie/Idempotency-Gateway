from fastapi import FastAPI
from app.store import IdempotencyStore
from pydantic import BaseModel

class PaymentRequest(BaseModel):
    amount: int
    currency: str


app = FastAPI(title="Idempotency Gateway")

store = IdempotencyStore()

@app.get("/health")
def health_check():
    return {"status": "ok"}
