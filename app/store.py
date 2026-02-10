from typing import Dict, Any
from threading import Lock
import time

class IdempotencyStore:
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()

    def get(self, key: str):
        return self._store.get(key)

    def set_processing(self, key: str, request_hash: str):
        with self._lock:
            self._store[key] = {
                "request_hash": request_hash,
                "status": "processing",
                "response_body": None,
                "response_code": None,
                "created_at": time.time()
            }

    def set_completed(self, key: str, response_body: Any, response_code: int):
        with self._lock:
            self._store[key]["status"] = "completed"
            self._store[key]["response_body"] = response_body
            self._store[key]["response_code"] = response_code

    def exists(self, key: str) -> bool:
        return key in self._store
