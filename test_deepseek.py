#!/usr/bin/env python3
"""
Test script for DeepSeek integration
Run this to verify the DeepSeek API client works correctly
"""

import os
import sys
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_deepseek_client():
    """Test the DeepSeek client functionality"""
    print("🧪 Testing DeepSeek Integration...")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ DEEPSEEK_API_KEY environment variable not set")
        print("   Set it to test the integration:")
        print("   export DEEPSEEK_API_KEY='your-api-key-here'")
        return False
    
    print(f"✅ DEEPSEEK_API_KEY found: {api_key[:8]}...")
    
    try:
        # Import the DeepSeek client
        from deepseek_client import DeepSeekClient, deepseek_client
        
        print("✅ DeepSeek client imported successfully")
        
        # Test client initialization
        client = DeepSeekClient()
        print("✅ DeepSeek client initialized")
        
        # Test simple chat completion
        print("\n📝 Testing chat completion...")
        response = client.chat_completion("Hello, this is a test message.")
        
        if response:
            print("✅ Chat completion successful!")
            print(f"Response: {response[:100]}...")
        else:
            print("❌ Chat completion failed")
            return False
        
        # Test with context
        print("\n📊 Testing with context...")
        context = {
            "user_id": "test_user",
            "channel_id": "test_channel",
            "query_type": "test"
        }
        
        response_with_context = client.chat_completion(
            "Tell me about fundraising strategy", 
            context=context
        )
        
        if response_with_context:
            print("✅ Context-aware chat completion successful!")
            print(f"Response: {response_with_context[:100]}...")
        else:
            print("❌ Context-aware chat completion failed")
            return False
        
        print("\n🎉 All DeepSeek tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_health_endpoint():
    """Test the health endpoint DeepSeek integration"""
    print("\n🏥 Testing Health Endpoint DeepSeek Integration...")
    print("=" * 50)
    
    try:
        from app import app
        from deepseek_client import deepseek_client
        
        with app.test_client() as client:
            response = client.get('/health')
            data = response.get_json()
            
            print(f"✅ Health endpoint status: {data.get('status')}")
            print(f"✅ DeepSeek API status: {data.get('components', {}).get('deepseek_api')}")
            
            if 'deepseek_api' in data.get('components', {}):
                print("✅ DeepSeek component found in health check")
                return True
            else:
                print("❌ DeepSeek component missing from health check")
                return False
                
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def test_debug_endpoint():
    """Test the DeepSeek debug endpoint"""
    print("\n🐛 Testing DeepSeek Debug Endpoint...")
    print("=" * 50)
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test without API key (should return 503)
            response = client.post('/debug/test-deepseek', 
                                json={"message": "test"})
            
            if response.status_code == 503:
                print("✅ Debug endpoint correctly returns 503 when DeepSeek not configured")
            else:
                print(f"⚠️  Unexpected status code: {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"❌ Debug endpoint test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DeepSeek Integration Test Suite")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("DeepSeek Client", test_deepseek_client),
        ("Health Endpoint", test_health_endpoint),
        ("Debug Endpoint", test_debug_endpoint)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! DeepSeek integration is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)
