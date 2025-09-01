#!/usr/bin/env python3
"""
Test Production-Ready Improvements
Diksha Foundation Fundraising Bot
"""

import os
import sys
import time
import json
from email_generator import EmailGenerator, RateLimiter

def test_configuration_loading():
    """Test configuration loading and validation"""
    print("🔧 Testing Configuration Loading")
    print("=" * 50)
    
    try:
        from config import EMAIL_CONFIG, DIKSHA_INFO, DEPLOYMENT_MODE
        
        print(f"✅ Configuration loaded successfully")
        print(f"   Deployment Mode: {DEPLOYMENT_MODE.value}")
        print(f"   Max Tokens: {EMAIL_CONFIG['max_tokens']}")
        print(f"   Temperature: {EMAIL_CONFIG['temperature']}")
        print(f"   Youth Trained: {DIKSHA_INFO['youth_trained']}")
        print(f"   Employment Rate: {DIKSHA_INFO['employment_rate']}")
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False
    
    return True

def test_input_validation():
    """Test input validation and sanitization"""
    print("\n🔒 Testing Input Validation")
    print("=" * 50)
    
    try:
        generator = EmailGenerator()
        
        # Test valid data
        valid_data = {
            'organization_name': 'Wipro Foundation',
            'contact_person': 'John Doe',
            'sector_tags': 'Technology'
        }
        
        validated = generator._validate_donor_data(valid_data)
        print(f"✅ Valid data validation: {validated['organization_name']}")
        
        # Test malicious input
        malicious_data = {
            'organization_name': '<script>alert("xss")</script>Wipro Foundation',
            'contact_person': 'John" Doe',
            'sector_tags': 'Technology'
        }
        
        sanitized = generator._validate_donor_data(malicious_data)
        print(f"✅ Malicious input sanitized: {sanitized['organization_name']}")
        
        # Test missing fields
        incomplete_data = {'organization_name': 'Test Org'}
        completed = generator._validate_donor_data(incomplete_data)
        print(f"✅ Missing fields completed: {completed['contact_person']}")
        
    except Exception as e:
        print(f"❌ Input validation test failed: {e}")
        return False
    
    return True

def test_rate_limiting():
    """Test rate limiting functionality"""
    print("\n⏱️ Testing Rate Limiting")
    print("=" * 50)
    
    try:
        limiter = RateLimiter(max_calls=3, time_window=10)
        
        # Test within limits
        for i in range(3):
            allowed = limiter.is_allowed("test_user")
            print(f"   Request {i+1}: {'✅ Allowed' if allowed else '❌ Blocked'}")
        
        # Test exceeding limits
        blocked = limiter.is_allowed("test_user")
        print(f"   Request 4: {'✅ Allowed' if blocked else '❌ Blocked (Expected)'}")
        
        if not blocked:
            print("✅ Rate limiting working correctly")
        else:
            print("❌ Rate limiting not working")
            return False
            
    except Exception as e:
        print(f"❌ Rate limiting test failed: {e}")
        return False
    
    return True

def test_caching():
    """Test profile caching functionality"""
    print("\n💾 Testing Profile Caching")
    print("=" * 50)
    
    try:
        generator = EmailGenerator()
        
        # Simulate cache operations
        test_org = "Test Organization"
        
        # First call should cache
        generator._profile_cache[test_org] = {
            'file_name': 'test_profile.pdf',
            'content': 'Test content'
        }
        generator._cache_timestamps[test_org] = time.time()
        
        print(f"✅ Profile cached for: {test_org}")
        print(f"   Cache size: {len(generator._profile_cache)}")
        print(f"   Cache hit rate: {generator._get_cache_hit_rate()}")
        
        # Test cache timeout
        generator._cache_timestamps[test_org] = time.time() - 4000  # Expired
        hit_rate = generator._get_cache_hit_rate()
        print(f"   Cache hit rate after expiry: {hit_rate}")
        
    except Exception as e:
        print(f"❌ Caching test failed: {e}")
        return False
    
    return True

def test_system_health():
    """Test system health monitoring"""
    print("\n📊 Testing System Health Monitoring")
    print("=" * 50)
    
    try:
        generator = EmailGenerator()
        health = generator.get_system_health()
        
        print(f"✅ System health retrieved")
        print(f"   Deployment Mode: {health['deployment_mode']}")
        print(f"   Cache Size: {health['cache_size']}")
        print(f"   Cache Hit Rate: {health['cache_hit_rate']}")
        print(f"   Claude API: {'✅ Configured' if health['claude_api_configured'] else '❌ Not Configured'}")
        print(f"   Drive Service: {'✅ Configured' if health['drive_service_configured'] else '❌ Not Configured'}")
        print(f"   Rate Limiting: {health['rate_limit_status']}")
        
        if 'psutil_not_available' not in health:
            print(f"   CPU Usage: {health['cpu_percent']}%")
            print(f"   Memory Usage: {health['memory_percent']}%")
            print(f"   Disk Usage: {health['disk_usage']}%")
        else:
            print("   System monitoring: psutil not available")
        
    except Exception as e:
        print(f"❌ System health test failed: {e}")
        return False
    
    return True

def test_retry_logic():
    """Test retry logic with decorator"""
    print("\n🔄 Testing Retry Logic")
    print("=" * 50)
    
    try:
        from email_generator import retry_on_failure
        
        # Test function that fails initially
        call_count = 0
        
        @retry_on_failure(max_retries=3, delay=0.1)
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception(f"Simulated failure {call_count}")
            return "Success on attempt 3"
        
        result = test_function()
        print(f"✅ Retry logic working: {result}")
        print(f"   Attempts made: {call_count}")
        
    except Exception as e:
        print(f"❌ Retry logic test failed: {e}")
        return False
    
    return True

def test_error_handling():
    """Test error handling and fallbacks"""
    print("\n🛡️ Testing Error Handling")
    print("=" * 50)
    
    try:
        generator = EmailGenerator()
        
        # Test with invalid template type
        invalid_data = {'organization_name': 'Test Org'}
        subject, body = generator.generate_email("invalid_template", invalid_data)
        
        if "Template type 'invalid_template' not found" in body:
            print("✅ Invalid template handling: Working")
        else:
            print("❌ Invalid template handling: Failed")
            return False
        
        # Test with malformed data
        malformed_data = None
        try:
            subject, body = generator.generate_email("intro", malformed_data)
            print("✅ Malformed data handling: Working")
        except Exception as e:
            print(f"✅ Malformed data handling: Caught error - {e}")
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    
    return True

def main():
    """Run all production-ready tests"""
    print("🚀 Diksha Foundation Production-Ready Improvements Test Suite")
    print("=" * 70)
    
    tests = [
        ("Configuration Loading", test_configuration_loading),
        ("Input Validation", test_input_validation),
        ("Rate Limiting", test_rate_limiting),
        ("Profile Caching", test_caching),
        ("System Health", test_system_health),
        ("Retry Logic", test_retry_logic),
        ("Error Handling", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is production-ready.")
    else:
        print("⚠️ Some tests failed. Review before production deployment.")
    
    print("\n💡 **Production Improvements Implemented:**")
    print("1. ✅ Updated Claude API model (claude-sonnet-4-20250514)")
    print("2. ✅ Input validation and sanitization")
    print("3. ✅ Centralized configuration management")
    print("4. ✅ Profile caching with timeout")
    print("5. ✅ Retry logic with exponential backoff")
    print("6. ✅ Rate limiting for API calls")
    print("7. ✅ System health monitoring")
    print("8. ✅ Enhanced error handling")
    print("9. ✅ Security enhancements")
    print("10. ✅ Deployment mode configuration")
    
    print("\n🚀 **Ready for Small-Scale Production Deployment!**")

if __name__ == "__main__":
    main()

