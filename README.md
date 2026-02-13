## Architecture Diagram

# Idempotency Gateway (Pay-Once Protocol)

A RESTful API that ensures payment requests are processed **exactly once**, preventing double-charges.

---

## 1. Architecture Diagram

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Store

    Client->>API: POST /process-payment + Idempotency-Key
    API->>Store: check(key)
    alt key not exist
        Store-->>API: None
        API->>Store: set_processing(key)
        API-->>Client: 201 Created (after processing)
        Store-->>Store: set_completed(key, response)
    else key exists
        alt different body
            API-->>Client: 409 Conflict
        else processing
            API->>Store: wait_until_completed(key)
            Store-->>API: completed response
            API-->>Client: replay response + X-Cache-Hit
        else completed
            API-->>Client: replay response + X-Cache-Hit
        end
    end



# Idempotency Gateway (Pay-Once Protocol)
A backend service that ensures payment requests are processed exactly once using an Idempotency-Key mechanism.

2. Setup Instructions
Clone the repo:
git clone <your-forked-repo-url>
cd Idempotency-Gateway


Create virtual environment & install dependencies:
python -m venv venv
# Activate venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate

pip install fastapi uvicorn pydantic

Run the API:
uvicorn app.main:app --reload
Test health endpoint:
GET http://127.0.0.1:8000/health

3. API Documentation
Endpoint: /process-payment
Method	Header	Body	Success Response
POST	Idempotency-Key: <string>	{ "amount": 100, "currency": "GHS" }	201 Created { "message": "Charged 100 GHS" }
Duplicate Request (same key & body):
Response: same as first request
Header: X-Cache-Hit: true
Conflict Request (same key, different body):
Response: 409 Conflict
Message: "Idempotency key already used for a different request body."
In-flight Requests:
Multiple identical requests processed safely
Only first request runs processing, others wait until completion

4. Design Decisions
In-memory store (IdempotencyStore) for simplicity and thread-safety with Lock
Request body hashing to detect different payloads
wait_until_completed for handling simultaneous requests (Bonus Story)
TTL to expire old keys after 5 minutes and prevent memory bloat
FastAPI + Pydantic for clean validation and modern API structure

5. Developer’s Choice Feature
TTL expiration for completed requests:
Completed idempotency keys expire after 5 minutes
Ensures memory is not overloaded
Late retries are treated as new requests, safe for real-world usage


.Conclusion
This API demonstrates a robust, production-ready idempotency layer suitable for fintech payment systems.
Handles duplicate and simultaneous requests
Prevents double charging
Maintains data integrity with conflict detection
Prevents memory bloat with TTL expiration


