"""
cache.py — Smart TTL-based in-memory cache for expensive AI computations.

Design decisions:
  - Uses cachetools.TTLCache (thread-safe via a RLock wrapper).
  - Cache key is a stable hash of the user's profile fields so that any
    profile update automatically invalidates that user's cached results.
  - The interface is intentionally Redis-compatible: swap the backend by
    changing the get/set implementation without touching any call sites.
  - TTL values are environment-configurable so staging can use shorter
    windows without code changes.

Cached operations and their TTLs (default):
  - predict_placement   : 10 min  (fast compute, changes with profile)
  - recommend_companies : 15 min  (pure heuristic, stable)
  - skill_gap_analysis  : 10 min  (NLP model — expensive)
  - roadmap             : 20 min  (most expensive — graph traversal + NLP)
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
