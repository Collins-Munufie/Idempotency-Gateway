import hashlib
import json
from typing import Any

def hash_request_body(body: Any) -> str:
    """
    Generate a deterministic hash of the request body.
    Ensures same logical payload produces same hash.
    """
    normalized = json.dumps(body, sort_keys=True)
    return hashlib.sha256(normalized.encode()).hexdigest()
