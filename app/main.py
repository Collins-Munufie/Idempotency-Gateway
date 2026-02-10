from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
import time

from app.store import IdempotencyStore
from app.utils import hash_request_body

app = FastAPI(title="Idempotency Gateway")

store = IdempotencyStore()

class PaymentRequest(BaseModel):
    amount: int
    currency: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/process-payment", status_code=201)
def process_payment(
    payload: PaymentRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    # 1. Validate Idempotency-Key
    if not idempotency_key:
        raise HTTPException(
            status_code=400,
            detail="Idempotency-Key header is required"
        )

    # 2. Temporary guard (duplicates handled in next step)
    if store.exists(idempotency_key):
        raise HTTPException(
            status_code=400,
            detail="Duplicate handling not implemented yet"
        )

    # 3. Hash request body
    request_hash = hash_request_body(payload.dict())

    # 4. Mark as processing
    store.set_processing(idempotency_key, request_hash)

    # 5. Simulate payment processing
    time.sleep(2)

    # 6. Build response
    response_body = {
        "message": f"Charged {payload.amount} {payload.currency}"
    }

    # 7. Mark as completed
    store.set_completed(
        idempotency_key,
        response_body=response_body,
        response_code=201
    )

    return response_body
