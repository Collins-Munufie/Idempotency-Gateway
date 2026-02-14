## 2. Setup Instructions

1. Create virtual environment:
python -m venv venv

2. Install dependencies:
pip install fastapi uvicorn pydantic

3. Run the server:
uvicorn app.main:app --reload

4. Open in browser:
http://127.0.0.1:8000/docs


## 3. API

### POST /process-payment

Header:
Idempotency-Key: <string>

Body:
{
  "amount": 100,
  "currency": "GHS"
}

Success:
201 Created
{
  "message": "Charged 100 GHS"
}

Duplicate request:
- Same response
- X-Cache-Hit: true

Conflict:
409 Conflict


## 4. Design Decisions

- In-memory idempotency store
- Request body hashing to detect conflicts
- Lock for thread safety
- Wait mechanism for in-flight requests
- TTL expiration (Developer’s Choice)




# Idempotency Gateway (Pay-Once Protocol) A RESTful API that ensures payment requests are processed **exactly once**, preventing double-charges. --- ## 1. Architecture Diagram
mermaid
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