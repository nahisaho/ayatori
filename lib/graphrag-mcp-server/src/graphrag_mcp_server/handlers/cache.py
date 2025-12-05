"""Caching utilities for GraphRAG MCP Server.

Provides simple in-memory caching for search results
to improve performance for repeated queries.
"""

import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    """A cached item with metadata."""

    value: T
    created_at: float
    expires_at: float
    hits: int = 0

    @property
    def is_expired(self) -> bool:
        """Check if the entry has expired."""
        return time.time() > self.expires_at

    def touch(self) -> None:
        """Record a cache hit."""
        self.hits += 1


@dataclass
class CacheStats:
    """Cache statistics."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "size": self.size,
            "hit_rate": f"{self.hit_rate:.2%}",
        }


class SearchCache:
    """In-memory cache for search results.

    Provides TTL-based caching with automatic cleanup
    and size limits.
    """

    def __init__(
        self,
        max_size: int = 100,
        default_ttl: float = 300.0,  # 5 minutes
        cleanup_interval: float = 60.0,  # 1 minute
    ):
        """Initialize the cache.

        Args:
            max_size: Maximum number of entries to store.
            default_ttl: Default time-to-live in seconds.
            cleanup_interval: Interval for cleanup task.
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        self._cache: dict[str, CacheEntry[Any]] = {}
        self._stats = CacheStats()
        self._lock = asyncio.Lock()
        self._cleanup_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """Start the background cleanup task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.debug("Cache cleanup task started")

    async def stop(self) -> None:
        """Stop the background cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            logger.debug("Cache cleanup task stopped")

    async def get(self, key: str) -> Any | None:
        """Get a value from the cache.

        Args:
            key: Cache key.

        Returns:
            Cached value or None if not found/expired.
        """
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._stats.misses += 1
                return None

            if entry.is_expired:
                del self._cache[key]
                self._stats.misses += 1
                self._stats.evictions += 1
                return None

            entry.touch()
            self._stats.hits += 1
            return entry.value

    async def set(
        self, key: str, value: Any, ttl: float | None = None
    ) -> None:
        """Store a value in the cache.

        Args:
            key: Cache key.
            value: Value to cache.
            ttl: Optional TTL override.
        """
        async with self._lock:
            # Evict oldest entries if at capacity
            while len(self._cache) >= self.max_size:
                await self._evict_oldest()

            now = time.time()
            self._cache[key] = CacheEntry(
                value=value,
                created_at=now,
                expires_at=now + (ttl or self.default_ttl),
            )
            self._stats.size = len(self._cache)

    async def delete(self, key: str) -> bool:
        """Delete an entry from the cache.

        Args:
            key: Cache key.

        Returns:
            True if entry was deleted, False if not found.
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats.size = len(self._cache)
                return True
            return False

    async def clear(self) -> None:
        """Clear all entries from the cache."""
        async with self._lock:
            self._cache.clear()
            self._stats.size = 0
            logger.debug("Cache cleared")

    async def _evict_oldest(self) -> None:
        """Evict the oldest entry (must be called with lock held)."""
        if not self._cache:
            return

        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].created_at,
        )
        del self._cache[oldest_key]
        self._stats.evictions += 1
        self._stats.size = len(self._cache)

    async def _cleanup_loop(self) -> None:
        """Background task to clean up expired entries."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")

    async def _cleanup_expired(self) -> None:
        """Remove all expired entries."""
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired
            ]
            for key in expired_keys:
                del self._cache[key]
                self._stats.evictions += 1

            if expired_keys:
                self._stats.size = len(self._cache)
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    def get_stats(self) -> CacheStats:
        """Get cache statistics.

        Returns:
            Current cache statistics.
        """
        return self._stats

    @staticmethod
    def make_key(
        search_type: str,
        query: str,
        **kwargs: Any,
    ) -> str:
        """Generate a cache key for a search query.

        Args:
            search_type: Type of search (global, local, drift).
            query: Search query string.
            **kwargs: Additional parameters.

        Returns:
            Unique cache key string.
        """
        # Sort kwargs for consistent ordering
        sorted_kwargs = sorted(kwargs.items())
        key_parts = [search_type, query] + [f"{k}={v}" for k, v in sorted_kwargs]
        key_string = "|".join(str(p) for p in key_parts)

        # Use hash for fixed-length keys
        return hashlib.sha256(key_string.encode()).hexdigest()[:32]


# Global cache instance
_search_cache: SearchCache | None = None


def get_search_cache() -> SearchCache:
    """Get or create the global search cache instance.

    Returns:
        The global SearchCache instance.
    """
    global _search_cache
    if _search_cache is None:
        _search_cache = SearchCache()
    return _search_cache


async def cached_search(
    search_type: str,
    query: str,
    search_func: Any,
    ttl: float | None = None,
    **kwargs: Any,
) -> Any:
    """Execute a search with caching.

    Args:
        search_type: Type of search.
        query: Search query.
        search_func: Async function to execute if cache miss.
        ttl: Optional cache TTL.
        **kwargs: Additional search parameters.

    Returns:
        Search result (from cache or fresh).
    """
    cache = get_search_cache()
    key = SearchCache.make_key(search_type, query, **kwargs)

    # Try cache first
    cached_result = await cache.get(key)
    if cached_result is not None:
        logger.debug(f"Cache hit for {search_type} query")
        return cached_result

    # Execute search
    result = await search_func(query, **kwargs)

    # Cache the result
    await cache.set(key, result, ttl)
    logger.debug(f"Cached {search_type} query result")

    return result
