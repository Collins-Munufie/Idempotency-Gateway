from typing import Dict, Any
from threading import Lock, Event
import time


class IdempotencyStore:
    def __init__(self, ttl: int = 300):
        """
        ttl: time in seconds to keep completed requests (default: 300s = 5 minutes)
        """
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self._events: Dict[str, Event] = {}
        self.ttl = ttl

    def get(self, key: str):
        with self._lock:
            record = self._store.get(key)
            if not record:
                return None

            # Only expire completed records
            if record["status"] == "completed":
                elapsed = time.time() - record["created_at"]
                if elapsed > self.ttl:
                    del self._store[key]
                    return None

            return record

    def set_processing(self, key: str, request_hash: str) -> bool:
        """
        Atomically mark a key as processing.
        Returns True if this call claimed the key, False if already taken.
        """
        with self._lock:
            # Double-check inside the lock to close the race window
            if key in self._store:
                return False
            event = Event()
            self._events[key] = event
            self._store[key] = {
                "request_hash": request_hash,
                "status": "processing",
                "response_body": None,
                "response_code": None,
                "created_at": time.time()
            }
            return True

    def set_completed(self, key: str, response_body: Any, response_code: int):
        with self._lock:
            self._store[key]["status"] = "completed"
            self._store[key]["response_body"] = response_body
            self._store[key]["response_code"] = response_code
            self._store[key]["created_at"] = time.time()
            # Signal any waiting threads
            event = self._events.pop(key, None)
        if event:
            event.set()

    def exists(self, key: str) -> bool:
        return key in self._store

    def wait_until_completed(self, key: str, timeout: float = 30.0):
        """
        Block until the given idempotency key finishes processing.
        Returns the record, or None if timeout exceeded.
        """
        event = self._events.get(key)
        if event:
            event.wait(timeout=timeout)

        record = self.get(key)
        if record and record["status"] == "completed":
            return record
        return None