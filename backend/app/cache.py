"""
cache.py — Smart TTL-based cache for expensive AI computations.

Supports two backends — selected automatically at startup:
  • Redis   : when REDIS_URL env var is set (production / multi-instance)
  • cachetools TTLCache : when REDIS_URL is absent (local dev / single-instance)

All call sites (routes.py) are identical regardless of backend — the
_NamespacedCache interface is the same for both.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ADR-001: In-Process Cache (cachetools) vs. Distributed Cache (Redis)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STATUS:    IMPLEMENTED — both backends ship in this file.
DATE:      2025-05-01
DECISION:  Auto-detect REDIS_URL; fall back to cachetools if absent.

WHY THIS DESIGN:
  1. Zero-config local dev — no Redis needed for development.
  2. Production-grade scaling — set REDIS_URL and Redis is used automatically.
  3. Shared cache across Gunicorn workers when Redis is active.
  4. Sub-microsecond latency (dict) in single-instance mode.
  5. All call sites unchanged — backend swap is transparent.

CONSEQUENCES:
  - Redis mode: cache survives process restarts; shared across N workers.
  - cachetools mode: cache is per-process; lost on restart (max 1 cold req/user).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
To activate Redis: set REDIS_URL=redis://redis:6379/0 in your .env
The docker-compose.yml redis service is already configured.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cached operations and their TTLs (default, env-configurable):
  - predict_placement   : 10 min  (fast compute, changes with profile)
  - recommend_companies : 15 min  (pure heuristic, stable)
  - skill_gap_analysis  : 10 min  (NLP model — expensive)
  - roadmap             : 20 min  (most expensive — graph traversal + NLP)
"""

import os
import json
import hashlib
import logging
import threading
from typing import Any, Optional

from cachetools import TTLCache

logger = logging.getLogger("placementpro.cache")

# ─── TTL Constants (seconds) — override via environment variables ──────────────
TTL_PREDICTION = int(os.environ.get("CACHE_TTL_PREDICTION", 600))   # 10 min
TTL_COMPANIES  = int(os.environ.get("CACHE_TTL_COMPANIES",  900))   # 15 min
TTL_SKILL_GAP  = int(os.environ.get("CACHE_TTL_SKILL_GAP",  600))   # 10 min
TTL_ROADMAP    = int(os.environ.get("CACHE_TTL_ROADMAP",    1200))  # 20 min

# Maximum entries per namespace (in-memory mode only)
_MAX_SIZE = int(os.environ.get("CACHE_MAX_SIZE", 256))

# ─── Redis Client (optional) ──────────────────────────────────────────────────
_REDIS_URL = os.environ.get("REDIS_URL", "").strip()
_redis_client = None

if _REDIS_URL:
    try:
        import redis as _redis_lib
        _redis_client = _redis_lib.from_url(
            _REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        # Verify the connection is live at startup
        _redis_client.ping()
        logger.info("Cache backend: Redis (%s)", _REDIS_URL.split("@")[-1])
    except Exception as exc:
        logger.warning(
            "Redis connection failed (%s) — falling back to cachetools TTLCache. "
            "Set REDIS_URL correctly to enable distributed caching.",
            exc,
        )
        _redis_client = None
else:
    logger.info("Cache backend: cachetools TTLCache (in-process). "
                "Set REDIS_URL to switch to Redis.")


# ─── Shared Fingerprint Helper ────────────────────────────────────────────────
def _user_fingerprint(user) -> str:
    """
    Build a stable, deterministic SHA-256 key from all profile fields that
    affect the cached result.  Any profile update automatically produces a
    different key, effectively invalidating the old entry without an explicit
    delete call.
    """
    fingerprint = {
        "id":          user.id,
        "cgpa":        user.cgpa,
        "skills":      sorted(user.skills.split(",")) if user.skills else [],
        "internships": user.internships_count,
        "projects":    user.projects_count,
        "designation": user.target_designation,
        "branch":      user.branch,
    }
    raw = json.dumps(fingerprint, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ─── Redis-backed Namespaced Cache ───────────────────────────────────────────
class _RedisNamespacedCache:
    """
    Redis implementation of the cache interface.
    Keys are namespaced as  "<name>:<fingerprint>[:<suffix>]"
    Values are JSON-serialised and stored with a TTL via SETEX.
    """

    def __init__(self, name: str, ttl: int):
        self.name = name
        self._ttl = ttl

    def _key(self, user, suffix: str = "") -> str:
        fp = _user_fingerprint(user)
        return f"{self.name}:{fp}{':' + suffix if suffix else ''}"

    def get(self, user, suffix: str = "") -> Optional[Any]:
        try:
            raw = _redis_client.get(self._key(user, suffix))
            return json.loads(raw) if raw is not None else None
        except Exception as exc:
            logger.warning("Redis GET failed: %s", exc)
            return None

    def set(self, user, value: Any, suffix: str = "") -> None:
        try:
            _redis_client.setex(self._key(user, suffix), self._ttl, json.dumps(value))
        except Exception as exc:
            logger.warning("Redis SET failed: %s", exc)

    def invalidate(self, user) -> None:
        """Delete all keys for this user+namespace using SCAN (avoids KEYS blocking)."""
        pattern = f"{self.name}:{_user_fingerprint(user)}*"
        try:
            for key in _redis_client.scan_iter(pattern, count=50):
                _redis_client.delete(key)
        except Exception as exc:
            logger.warning("Redis INVALIDATE failed: %s", exc)

    @property
    def size(self) -> int:
        try:
            return _redis_client.dbsize()
        except Exception:
            return -1

    @property
    def stats(self) -> dict:
        try:
            info = _redis_client.info("memory")
            return {
                "namespace":    self.name,
                "backend":      "redis",
                "ttl_secs":     self._ttl,
                "used_memory":  info.get("used_memory_human", "?"),
                "redis_url":    _REDIS_URL.split("@")[-1],  # hide credentials
            }
        except Exception:
            return {"namespace": self.name, "backend": "redis", "status": "error"}


# ─── cachetools-backed Namespaced Cache ───────────────────────────────────────
class _LocalNamespacedCache:
    """
    In-process TTLCache implementation — used when Redis is not configured.
    Thread-safe via a per-instance RLock.
    """

    def __init__(self, name: str, ttl: int, maxsize: int = _MAX_SIZE):
        self.name = name
        self._ttl = ttl
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._lock = threading.RLock()

    def _key(self, user, suffix: str = "") -> str:
        fp = _user_fingerprint(user)
        return f"{self.name}:{fp}{':' + suffix if suffix else ''}"

    def get(self, user, suffix: str = "") -> Optional[Any]:
        with self._lock:
            return self._cache.get(self._key(user, suffix))

    def set(self, user, value: Any, suffix: str = "") -> None:
        with self._lock:
            self._cache[self._key(user, suffix)] = value

    def invalidate(self, user) -> None:
        prefix = f"{self.name}:{_user_fingerprint(user)}"
        with self._lock:
            for k in [k for k in self._cache.keys() if k.startswith(prefix)]:
                self._cache.pop(k, None)

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._cache)

    @property
    def stats(self) -> dict:
        with self._lock:
            return {
                "namespace": self.name,
                "backend":   "cachetools",
                "size":      len(self._cache),
                "maxsize":   self._cache.maxsize,
                "ttl_secs":  self._cache.ttl,
            }


# ─── Factory: pick backend at module import time ──────────────────────────────
def _make_cache(name: str, ttl: int):
    if _redis_client is not None:
        return _RedisNamespacedCache(name, ttl=ttl)
    return _LocalNamespacedCache(name, ttl=ttl)


# ─── Singleton Cache Instances ────────────────────────────────────────────────
prediction_cache = _make_cache("pred", ttl=TTL_PREDICTION)
companies_cache  = _make_cache("comp", ttl=TTL_COMPANIES)
skill_gap_cache  = _make_cache("sgap", ttl=TTL_SKILL_GAP)
roadmap_cache    = _make_cache("road", ttl=TTL_ROADMAP)


# ─── Utility Functions ────────────────────────────────────────────────────────
def all_cache_stats() -> list:
    """Return stats for all caches — exposed via /ready endpoint."""
    return [c.stats for c in [prediction_cache, companies_cache,
                               skill_gap_cache, roadmap_cache]]


def invalidate_all_for_user(user) -> None:
    """Call this after a profile update to ensure stale data is never served."""
    for cache in [prediction_cache, companies_cache, skill_gap_cache, roadmap_cache]:
        cache.invalidate(user)
