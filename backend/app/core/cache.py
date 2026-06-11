import json
from functools import wraps
from time import monotonic
from typing import Any, Callable, Optional

try:
    import redis
except Exception:  # pragma: no cover
    redis = None

from app.core.config import get_settings


_memory_cache: dict[str, tuple[float, Any]] = {}
_redis_unavailable_until = 0.0


def clear_cache():
    _memory_cache.clear()

    client = _redis_client()
    if client is not None:
        try:
            for key in client.scan_iter("*"):
                client.delete(key)
        except Exception:
            pass


def _redis_client():
    global _redis_unavailable_until

    now = monotonic()
    if now < _redis_unavailable_until:
        return None

    if redis is None:
        return None

    try:
        client = redis.from_url(
            get_settings().redis_url,
            decode_responses=True,
            socket_connect_timeout=0.05,
            socket_timeout=0.05,
        )
        client.ping()
        return client
    except Exception:
        _redis_unavailable_until = now + 60
        return None


def cached(key: str, ttl: Optional[int] = None):
    ttl = ttl or get_settings().cache_ttl_seconds

    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            cache_key = f"{key}:{args}:{kwargs}"
            now = monotonic()
            memory_value = _memory_cache.get(cache_key)
            if memory_value and now - memory_value[0] < ttl:
                return memory_value[1]

            client = _redis_client()

            if client is not None:
                cached_value = client.get(cache_key)
                if cached_value:
                    value = json.loads(cached_value)
                    _memory_cache[cache_key] = (now, value)
                    return value

            value = fn(*args, **kwargs)
            _memory_cache[cache_key] = (now, value)

            if client is not None:
                client.setex(cache_key, ttl, json.dumps(value, default=str))

            return value

        return wrapper

    return decorator

