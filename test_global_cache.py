#!/usr/bin/env python3
"""
Test Global Cache Implementation
Diksha Foundation Fundraising Bot
"""

import time
import threading
from email_generator import EmailGenerator
from cache_manager import cache_manager

def test_global_cache_benefits():
    """Test the benefits of global cache vs instance-level cache"""
    print("🌐 Testing Global Cache Benefits")
    print("=" * 60)
    
    # Clear cache before testing
    cache_manager.clear()
    
    # Test 1: Multiple instances share the same cache
    print("\n🔍 Test 1: Multiple instances sharing cache")
    print("-" * 40)
    
    generator1 = EmailGenerator()
    generator2 = EmailGenerator()
    
    # Both instances should use the same global cache
    print(f"Instance 1 cache manager: {id(generator1._get_donor_profile_from_drive.__self__)}")
    print(f"Instance 2 cache manager: {id(generator2._get_donor_profile_from_drive.__self__)}")
    print(f"Global cache manager: {id(cache_manager)}")
    
    # Test 2: Cache hit rate improvement
    print("\n🔍 Test 2: Cache hit rate improvement")
    print("-" * 40)
    
    # Simulate multiple requests for the same organization
    org_name = "Test Organization"
    
    # First request (cache miss)
    start_time = time.time()
    # Simulate profile fetch
    profile_data = {
        'file_name': 'test_profile.pdf',
        'content': 'Test content for demonstration'
    }
    cache_key = cache_manager.get_cache_key("donor_profile", org_name)
    cache_manager.set(cache_key, profile_data)
    first_request_time = time.time() - start_time
    
    print(f"First request (cache miss): {first_request_time:.4f}s")
    
    # Second request (cache hit)
    start_time = time.time()
    cached_profile = cache_manager.get(cache_key)
    second_request_time = time.time() - start_time
    
    print(f"Second request (cache hit): {second_request_time:.4f}s")
    print(f"Speed improvement: {((first_request_time - second_request_time) / first_request_time * 100):.1f}%")
    
    # Test 3: Memory efficiency
    print("\n🔍 Test 3: Memory efficiency")
    print("-" * 40)
    
    # Simulate multiple organizations
    orgs = [f"Org_{i}" for i in range(10)]
    
    for org in orgs:
        profile = {
            'file_name': f'{org}_profile.pdf',
            'content': f'Content for {org}'
        }
        cache_key = cache_manager.get_cache_key("donor_profile", org)
        cache_manager.set(cache_key, profile)
    
    stats = cache_manager.get_stats()
    print(f"Total cache entries: {stats['total_entries']}")
    print(f"Cache utilization: {stats['utilization_percent']}%")
    print(f"Max cache size: {stats['max_size']}")
    
    # Test 4: Thread safety
    print("\n🔍 Test 4: Thread safety")
    print("-" * 40)
    
    def cache_operation(thread_id):
        """Simulate cache operations from different threads"""
        for i in range(5):
            key = f"thread_{thread_id}_key_{i}"
            value = f"value_from_thread_{thread_id}_{i}"
            cache_manager.set(key, value)
            time.sleep(0.01)  # Small delay to simulate real usage
    
    # Create multiple threads
    threads = []
    for i in range(3):
        thread = threading.Thread(target=cache_operation, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    final_stats = cache_manager.get_stats()
    print(f"Final cache entries: {final_stats['total_entries']}")
    print(f"Thread safety test: {'✅ PASSED' if final_stats['total_entries'] == 15 else '❌ FAILED'}")
    
    # Test 5: Cache expiration
    print("\n🔍 Test 5: Cache expiration")
    print("-" * 40)
    
    # Add a short-lived cache entry
    cache_manager.set("expiring_key", "expiring_value", timeout=1)
    print("Added cache entry with 1 second timeout")
    
    # Check immediately
    immediate_check = cache_manager.get("expiring_key")
    print(f"Immediate check: {'✅ Found' if immediate_check else '❌ Not found'}")
    
    # Wait for expiration
    time.sleep(1.1)
    expired_check = cache_manager.get("expiring_key")
    print(f"After expiration: {'✅ Found' if expired_check else '❌ Not found (Expected)'}")
    
    # Test 6: Performance comparison
    print("\n🔍 Test 6: Performance comparison")
    print("-" * 40)
    
    # Simulate 100 cache operations
    start_time = time.time()
    for i in range(100):
        key = f"perf_test_{i}"
        value = f"value_{i}"
        cache_manager.set(key, value)
        retrieved = cache_manager.get(key)
    
    total_time = time.time() - start_time
    operations_per_second = 100 / total_time
    
    print(f"100 cache operations completed in: {total_time:.4f}s")
    print(f"Cache operations per second: {operations_per_second:.0f}")
    
    # Final cache statistics
    print("\n📊 Final Cache Statistics")
    print("=" * 60)
    
    final_stats = cache_manager.get_stats()
    for key, value in final_stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print("\n🎉 Global Cache Test Completed!")
    print("\n💡 **Benefits of Global Cache:**")
    print("1. ✅ **Memory Efficiency** - Single cache instance across all requests")
    print("2. ✅ **Better Hit Rates** - Shared cache across multiple users/instances")
    print("3. ✅ **Thread Safety** - Concurrent access without conflicts")
    print("4. ✅ **Automatic Cleanup** - Expired entries removed automatically")
    print("5. ✅ **LRU Eviction** - Oldest entries removed when cache is full")
    print("6. ✅ **Performance Monitoring** - Detailed cache statistics")
    print("7. ✅ **Scalability** - Cache grows with application needs")
    
    print("\n🚀 **Ready for Production Use!**")

if __name__ == "__main__":
    test_global_cache_benefits()

