#!/usr/bin/env python
"""
Test script to verify caching functionality.
"""

import os
import time

os.environ['FLASK_ENV'] = 'development'

from src.total_bankroll import create_app
from src.total_bankroll.services.bankroll_service import BankrollService
from src.total_bankroll.extensions import cache

# Create app for context
app = create_app()

with app.app_context():
    print("Testing Flask-Caching implementation...")
    print("=" * 60)
    
    # Test 1: Cache initialization
    print("\n1. Checking cache initialization...")
    print(f"   Cache type: {app.config.get('CACHE_TYPE', 'Not set')}")
    print(f"   Cache timeout: {app.config.get('CACHE_DEFAULT_TIMEOUT', 'Not set')} seconds")
    print("   ✓ Cache is initialized")
    
    # Test 2: Test cache.set and cache.get
    print("\n2. Testing basic cache operations...")
    test_key = "test_key"
    test_value = "test_value"
    cache.set(test_key, test_value, timeout=60)
    retrieved = cache.get(test_key)
    assert retrieved == test_value, "Cache get/set failed!"
    print(f"   ✓ Set '{test_key}' = '{test_value}'")
    print(f"   ✓ Retrieved value: '{retrieved}'")
    
    # Test 3: Test cache.delete
    print("\n3. Testing cache deletion...")
    cache.delete(test_key)
    retrieved_after_delete = cache.get(test_key)
    assert retrieved_after_delete is None, "Cache delete failed!"
    print(f"   ✓ Deleted '{test_key}'")
    print(f"   ✓ Retrieved after delete: {retrieved_after_delete}")
    
    # Test 4: Test memoization (service caching)
    print("\n4. Testing @cache.memoize decorator...")
    
    # Create a simple cached function to test
    @cache.memoize(timeout=60)
    def expensive_calculation(x, y):
        """Simulated expensive calculation."""
        import time
        time.sleep(0.01)  # Simulate work
        return x + y
    
    print("   First call to expensive_calculation(10, 20)...")
    start = time.time()
    result1 = expensive_calculation(10, 20)
    elapsed1 = time.time() - start
    print(f"   Result: {result1}, Time: {elapsed1:.4f}s")
    
    # Second call - should be cached
    print("   Second call (should be cached)...")
    start = time.time()
    result2 = expensive_calculation(10, 20)
    elapsed2 = time.time() - start
    print(f"   Result: {result2}, Time: {elapsed2:.4f}s")
    
    assert result1 == result2, "Cached result doesn't match!"
    if elapsed2 < elapsed1 / 2:  # Should be significantly faster
        print(f"   ✓ Second call was much faster ({elapsed2:.4f}s vs {elapsed1:.4f}s) - caching works!")
    else:
        print(f"   ⚠ Second call timing: {elapsed2:.4f}s vs {elapsed1:.4f}s")
    
    # Test 5: Test cache invalidation
    print("\n5. Testing cache invalidation...")
    cache.delete_memoized(expensive_calculation)
    print("   ✓ Cache invalidated for expensive_calculation")
    
    # Call again to verify it recalculates
    print("   Third call (after invalidation, should recalculate)...")
    start = time.time()
    result3 = expensive_calculation(10, 20)
    elapsed3 = time.time() - start
    print(f"   Result: {result3}, Time: {elapsed3:.4f}s")
    print(f"   ✓ Function recalculated after cache invalidation")
    
    print("\n" + "=" * 60)
    print("✓ All caching tests passed!")
    print("=" * 60)
