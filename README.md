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
