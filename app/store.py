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
            self._store[key]["created_at"] = time.time()  # reset timestamp

    def exists(self, key: str) -> bool:
        return key in self._store

    def wait_until_completed(self, key: str, poll_interval: float = 0.05):
        """
        Block until the given idempotency key finishes processing.
        """
        while True:
            record = self.get(key)
            if record and record["status"] == "completed":
                return record
            time.sleep(poll_interval)


class IdempotencyStore:
    def __init__(self, ttl: int = 300):
        """
        ttl: time in seconds to keep completed requests
        default: 300s = 5 minutes
        """
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self.ttl = ttl

    def get(self, key: str):
        record = self._store.get(key)
        if not record:
            return None

        # Check TTL
        if record["status"] == "completed":
            elapsed = time.time() - record["created_at"]
            if elapsed > self.ttl:
                # Expire the key
                with self._lock:
                    del self._store[key]
                return None
        return record
