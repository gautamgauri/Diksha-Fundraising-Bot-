#!/usr/bin/env python3
"""
Global Cache Manager for Diksha Foundation Fundraising Bot
"""

import time
import threading
import logging
from typing import Dict, Any, Optional
from collections import OrderedDict
from config import CACHE_CONFIG

logger = logging.getLogger(__name__)

class GlobalCacheManager:
    """Thread-safe global cache manager for the entire application"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern for global cache"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize global cache manager"""
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        
        # Cache storage
        self._cache = OrderedDict()
        self._timestamps = {}
        self._access_counts = {}
        
        # Configuration
        self.max_size = CACHE_CONFIG['max_cache_size']
        self.cleanup_interval = CACHE_CONFIG['cleanup_interval']
        self.last_cleanup = time.time()
        
        # Thread safety
        self._cache_lock = threading.RLock()
        
        logger.info(f"GlobalCacheManager initialized with max_size={self.max_size}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with automatic expiry check"""
        with self._cache_lock:
            # Check if key exists and is not expired
            if key in self._cache:
                if self._is_expired(key):
                    self._remove(key)
                    return default
                
                # Update access count and move to end (LRU)
                self._access_counts[key] += 1
                self._cache.move_to_end(key)
                return self._cache[key]
            
            return default
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """Set value in cache with optional timeout"""
        with self._cache_lock:
            # Use default timeout if not specified
            if timeout is None:
                timeout = CACHE_CONFIG['profile_timeout']
            
            # Remove if already exists
            if key in self._cache:
                self._remove(key)
            
            # Check if we need to make space
            if len(self._cache) >= self.max_size:
                self._evict_oldest()
            
            # Add new entry
            self._cache[key] = value
            self._timestamps[key] = time.time() + timeout
            self._access_counts[key] = 1
            
            # Periodic cleanup
            self._maybe_cleanup()
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        with self._cache_lock:
            if key in self._cache:
                if self._is_expired(key):
                    self._remove(key)
                    return False
                return True
            return False
    
    def remove(self, key: str) -> bool:
        """Remove key from cache"""
        with self._cache_lock:
            return self._remove(key)
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._cache_lock:
            self._cache.clear()
            self._timestamps.clear()
            self._access_counts.clear()
            logger.info("Global cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._cache_lock:
            current_time = time.time()
            valid_entries = sum(1 for k in self._cache if not self._is_expired(k))
            expired_entries = len(self._cache) - valid_entries
            
            return {
                'total_entries': len(self._cache),
                'valid_entries': valid_entries,
                'expired_entries': expired_entries,
                'max_size': self.max_size,
                'utilization_percent': round((len(self._cache) / self.max_size) * 100, 1),
                'last_cleanup': self.last_cleanup,
                'cleanup_interval': self.cleanup_interval
            }
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        return time.time() > self._timestamps.get(key, 0)
    
    def _remove(self, key: str) -> bool:
        """Remove key from cache (internal method)"""
        if key in self._cache:
            del self._cache[key]
            del self._timestamps[key]
            del self._access_counts[key]
            return True
        return False
    
    def _evict_oldest(self) -> None:
        """Evict oldest cache entry (LRU)"""
        if self._cache:
            oldest_key = next(iter(self._cache))
            self._remove(oldest_key)
            logger.debug(f"Evicted oldest cache entry: {oldest_key}")
    
    def _maybe_cleanup(self) -> None:
        """Periodically cleanup expired entries"""
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_expired()
            self.last_cleanup = current_time
    
    def _cleanup_expired(self) -> None:
        """Remove all expired entries"""
        with self._cache_lock:
            expired_keys = [key for key in list(self._cache.keys()) if self._is_expired(key)]
            for key in expired_keys:
                self._remove(key)
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_cache_key(self, prefix: str, *args) -> str:
        """Generate consistent cache key from prefix and arguments"""
        # Create a hashable key from arguments
        key_parts = [prefix] + [str(arg) for arg in args]
        return "::".join(key_parts)

# Global instance
cache_manager = GlobalCacheManager()

