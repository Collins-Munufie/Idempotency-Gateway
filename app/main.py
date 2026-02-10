from fastapi import FastAPI

app = FastAPI(title="Idempotency Gateway")

@app.get("/health")
def health_check():
    return {"status": "ok"}
