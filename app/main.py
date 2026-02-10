from fastapi import FastAPI, Header, HTTPException, Response
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


@app.post("/process-payment")
def process_payment(
    payload: PaymentRequest,
    response: Response,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    # 1. Validate Idempotency-Key
    if not idempotency_key:
        raise HTTPException(
            status_code=400,
            detail="Idempotency-Key header is required"
        )

    # 2. Hash request body
    request_hash = hash_request_body(payload.dict())

    existing = store.get(idempotency_key)

    # 3. Key already exists
    if existing:
        # 3a. Same key, different body → conflict
        if existing["request_hash"] != request_hash:
            raise HTTPException(
                status_code=409,
                detail="Idempotency key already used for a different request body."
            )

        # 3b. In-flight request → wait
        if existing["status"] == "processing":
            record = store.wait_until_completed(idempotency_key)
            response.headers["X-Cache-Hit"] = "true"
            response.status_code = record["response_code"]
            return record["response_body"]

        # 3c. Completed request → replay
        response.headers["X-Cache-Hit"] = "true"
        response.status_code = existing["response_code"]
        return existing["response_body"]

    # 4. First-time request
    store.set_processing(idempotency_key, request_hash)

    # 5. Simulate payment processing
    time.sleep(2)

    response_body = {
        "message": f"Charged {payload.amount} {payload.currency}"
    }

    store.set_completed(
        idempotency_key,
        response_body=response_body,
        response_code=201
    )

    response.status_code = 201
    return response_body
