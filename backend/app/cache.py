"""
cache.py — Smart TTL-based in-memory cache for expensive AI computations.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ADR-001: In-Process Cache (cachetools) vs. Distributed Cache (Redis)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STATUS:    Accepted — revisit if horizontal scaling is required.
DATE:      2025-05-01
CONTEXT:   PlacementPro+ deploys as a single-instance Gunicorn/Docker
           container on Render.com / HuggingFace Spaces. The ML inference
           workload (sentence-transformers + graph pathfinding) is CPU-bound
           and benefits from caching its outputs.

DECISION:  Use cachetools.TTLCache (in-process, single-node) instead of Redis.

RATIONALE:
  1. Zero infrastructure overhead — no Redis container, no broker config,
     no additional service in docker-compose.yml.
  2. Sub-microsecond latency — dictionary lookup vs ~1ms network round-trip
     to a Redis socket.
  3. Sufficient for single-instance deployments: all requests hit the same
     process, so cache entries are always shared across concurrent workers
     in a single Gunicorn worker-thread (sync workers share memory).
  4. The API surface is intentionally Redis-compatible (see below), so the
     migration cost to Redis is minimal when horizontal scaling is needed.

CONSEQUENCES:
  - Cache is NOT shared across multiple Gunicorn processes (multi-worker mode).
    With sync workers and a single instance, this is not an issue.
  - Cache is lost on process restart — TTL-based invalidation means this
    causes at most one "cold" request per user per restart cycle.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REDIS UPGRADE PATH (when horizontal scaling is needed)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1 — Add Redis dependency:
    pip install redis
    # In requirements.txt:  redis==5.x

Step 2 — Set env var in production:
    REDIS_URL=redis://redis:6379/0

Step 3 — Swap _NamespacedCache backend (ONLY change needed in this file):

    import redis as _redis
    _redis_client = _redis.from_url(os.environ.get("REDIS_URL", ""))

    class _NamespacedCache:
        def get(self, user, suffix=""):
            return json.loads(_redis_client.get(self._key(user, suffix)) or "null")

        def set(self, user, value, suffix=""):
            _redis_client.setex(self._key(user, suffix), self._ttl, json.dumps(value))

        def invalidate(self, user):
            pattern = f"{self.name}:{self._user_fingerprint(user)}*"
            for key in _redis_client.scan_iter(pattern):
                _redis_client.delete(key)

Step 4 — Add Redis service to docker-compose.yml:
    redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
        command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru

All call sites (routes.py) remain completely unchanged.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cached operations and their TTLs (default, env-configurable):
  - predict_placement   : 10 min  (fast compute, changes with profile)
  - recommend_companies : 15 min  (pure heuristic, stable)
  - skill_gap_analysis  : 10 min  (NLP model — expensive)
  - roadmap             : 20 min  (most expensive — graph traversal + NLP)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import json
import hashlib
import threading
from typing import Any, Optional

from cachetools import TTLCache


# ─── TTL Constants (seconds) — override via environment variables ──────────────
TTL_PREDICTION  = int(os.environ.get("CACHE_TTL_PREDICTION",  600))   # 10 min
TTL_COMPANIES   = int(os.environ.get("CACHE_TTL_COMPANIES",   900))   # 15 min
TTL_SKILL_GAP   = int(os.environ.get("CACHE_TTL_SKILL_GAP",   600))   # 10 min
TTL_ROADMAP     = int(os.environ.get("CACHE_TTL_ROADMAP",     1200))  # 20 min

# Maximum number of distinct cache entries per namespace
_MAX_SIZE = int(os.environ.get("CACHE_MAX_SIZE", 256))


# ─── Cache Namespaces ─────────────────────────────────────────────────────────
class _NamespacedCache:
    """
    Thin wrapper around TTLCache that adds:
    - A per-instance RLock for thread safety
    - Namespaced keys (so all caches can coexist in one dict if needed)
    - Stable profile fingerprinting
    """

    def __init__(self, name: str, ttl: int, maxsize: int = _MAX_SIZE):
        self.name = name
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._lock = threading.RLock()

    @staticmethod
    def _user_fingerprint(user) -> str:
        """
        Build a stable, deterministic key from fields that affect the result.
        If any of these change, the cache entry is effectively invalidated
        because the key changes.
        """
        fingerprint = {
            "id":            user.id,
            "cgpa":          user.cgpa,
            "skills":        sorted(user.skills.split(",")) if user.skills else [],
            "internships":   user.internships_count,
            "projects":      user.projects_count,
            "designation":   user.target_designation,
            "branch":        user.branch,
        }
        raw = json.dumps(fingerprint, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _key(self, user, suffix: str = "") -> str:
        return f"{self.name}:{self._user_fingerprint(user)}{':' + suffix if suffix else ''}"

    def get(self, user, suffix: str = "") -> Optional[Any]:
        with self._lock:
            return self._cache.get(self._key(user, suffix))

    def set(self, user, value: Any, suffix: str = "") -> None:
        with self._lock:
            self._cache[self._key(user, suffix)] = value

    def invalidate(self, user) -> None:
        """Manually invalidate all entries for a user (e.g. after profile update)."""
        prefix = f"{self.name}:{self._user_fingerprint(user)}"
        with self._lock:
            keys_to_delete = [k for k in self._cache.keys() if k.startswith(prefix)]
            for k in keys_to_delete:
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
                "size":      len(self._cache),
                "maxsize":   self._cache.maxsize,
                "ttl_secs":  self._cache.ttl,
            }


# ─── Singleton Cache Instances ────────────────────────────────────────────────
prediction_cache  = _NamespacedCache("pred",   ttl=TTL_PREDICTION)
companies_cache   = _NamespacedCache("comp",   ttl=TTL_COMPANIES)
skill_gap_cache   = _NamespacedCache("sgap",   ttl=TTL_SKILL_GAP)
roadmap_cache     = _NamespacedCache("road",   ttl=TTL_ROADMAP)


def all_cache_stats() -> list:
    """Return stats for all caches — exposed via /ready and /api/docs."""
    return [c.stats for c in [prediction_cache, companies_cache, skill_gap_cache, roadmap_cache]]


def invalidate_all_for_user(user) -> None:
    """Call this after a profile update to ensure stale data is never served."""
    for cache in [prediction_cache, companies_cache, skill_gap_cache, roadmap_cache]:
        cache.invalidate(user)
