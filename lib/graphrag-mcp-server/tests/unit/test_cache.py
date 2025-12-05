"""Tests for search cache."""

import pytest
import asyncio

from graphrag_mcp_server.handlers.cache import (
    CacheEntry,
    CacheStats,
    SearchCache,
    get_search_cache,
    cached_search,
)


class TestCacheEntry:
    """Tests for CacheEntry dataclass."""

    def test_entry_creation(self):
        """Should create entry with all fields."""
        import time
        now = time.time()
        entry = CacheEntry(
            value="test",
            created_at=now,
            expires_at=now + 60,
        )
        assert entry.value == "test"
        assert entry.hits == 0

    def test_entry_not_expired(self):
        """Should not be expired when within TTL."""
        import time
        now = time.time()
        entry = CacheEntry(
            value="test",
            created_at=now,
            expires_at=now + 60,
        )
        assert not entry.is_expired

    def test_entry_expired(self):
        """Should be expired after TTL."""
        import time
        now = time.time()
        entry = CacheEntry(
            value="test",
            created_at=now - 120,
            expires_at=now - 60,
        )
        assert entry.is_expired

    def test_entry_touch(self):
        """Should increment hits on touch."""
        import time
        now = time.time()
        entry = CacheEntry(
            value="test",
            created_at=now,
            expires_at=now + 60,
        )
        entry.touch()
        assert entry.hits == 1


class TestCacheStats:
    """Tests for CacheStats dataclass."""

    def test_stats_defaults(self):
        """Should have zero defaults."""
        stats = CacheStats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.evictions == 0
        assert stats.size == 0

    def test_hit_rate_zero_total(self):
        """Should return 0 for no requests."""
        stats = CacheStats()
        assert stats.hit_rate == 0.0

    def test_hit_rate_calculation(self):
        """Should calculate hit rate correctly."""
        stats = CacheStats(hits=75, misses=25)
        assert stats.hit_rate == 0.75

    def test_to_dict(self):
        """Should convert to dictionary."""
        stats = CacheStats(hits=10, misses=5)
        d = stats.to_dict()
        assert d["hits"] == 10
        assert d["misses"] == 5
        assert "hit_rate" in d


class TestSearchCache:
    """Tests for SearchCache class."""

    def test_cache_creation(self):
        """Should create cache with defaults."""
        cache = SearchCache()
        assert cache.max_size == 100
        assert cache.default_ttl == 300.0

    def test_cache_custom_settings(self):
        """Should accept custom settings."""
        cache = SearchCache(max_size=50, default_ttl=60.0)
        assert cache.max_size == 50
        assert cache.default_ttl == 60.0

    @pytest.mark.asyncio
    async def test_set_and_get(self):
        """Should store and retrieve values."""
        cache = SearchCache()
        await cache.set("key1", "value1")
        result = await cache.get("key1")
        assert result == "value1"

    @pytest.mark.asyncio
    async def test_get_missing_key(self):
        """Should return None for missing key."""
        cache = SearchCache()
        result = await cache.get("missing")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete(self):
        """Should delete entries."""
        cache = SearchCache()
        await cache.set("key1", "value1")
        deleted = await cache.delete("key1")
        assert deleted
        result = await cache.get("key1")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_missing(self):
        """Should return False for missing key."""
        cache = SearchCache()
        deleted = await cache.delete("missing")
        assert not deleted

    @pytest.mark.asyncio
    async def test_clear(self):
        """Should clear all entries."""
        cache = SearchCache()
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.clear()
        assert await cache.get("key1") is None
        assert await cache.get("key2") is None

    @pytest.mark.asyncio
    async def test_expired_entry(self):
        """Should not return expired entries."""
        cache = SearchCache()
        await cache.set("key1", "value1", ttl=0.01)  # Very short TTL
        await asyncio.sleep(0.02)
        result = await cache.get("key1")
        assert result is None

    @pytest.mark.asyncio
    async def test_eviction_at_capacity(self):
        """Should evict oldest when at capacity."""
        cache = SearchCache(max_size=3)
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")
        await cache.set("key4", "value4")  # Should evict key1
        
        assert await cache.get("key1") is None
        assert await cache.get("key4") == "value4"

    def test_make_key(self):
        """Should generate consistent keys."""
        key1 = SearchCache.make_key("global", "query", level=2)
        key2 = SearchCache.make_key("global", "query", level=2)
        assert key1 == key2

    def test_make_key_different_params(self):
        """Should generate different keys for different params."""
        key1 = SearchCache.make_key("global", "query", level=1)
        key2 = SearchCache.make_key("global", "query", level=2)
        assert key1 != key2

    def test_get_stats(self):
        """Should return stats object."""
        cache = SearchCache()
        stats = cache.get_stats()
        assert isinstance(stats, CacheStats)


class TestGetSearchCache:
    """Tests for get_search_cache function."""

    def test_returns_cache_instance(self):
        """Should return a SearchCache instance."""
        cache = get_search_cache()
        assert isinstance(cache, SearchCache)

    def test_returns_same_instance(self):
        """Should return same global instance."""
        cache1 = get_search_cache()
        cache2 = get_search_cache()
        assert cache1 is cache2


class TestCachedSearch:
    """Tests for cached_search function."""

    @pytest.mark.asyncio
    async def test_caches_result(self):
        """Should cache search results."""
        call_count = 0

        async def mock_search(query, **kwargs):
            nonlocal call_count
            call_count += 1
            return f"result for {query}"

        # First call
        result1 = await cached_search("global", "test", mock_search)
        # Second call (should be cached)
        result2 = await cached_search("global", "test", mock_search)

        assert result1 == result2
        assert call_count == 1  # Only called once

    @pytest.mark.asyncio
    async def test_different_queries_not_cached(self):
        """Should not return cached result for different query."""
        call_count = 0

        async def mock_search(query, **kwargs):
            nonlocal call_count
            call_count += 1
            return f"result for {query}"

        await cached_search("global", "query1", mock_search)
        await cached_search("global", "query2", mock_search)

        assert call_count == 2
