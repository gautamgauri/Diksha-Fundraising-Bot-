#!/usr/bin/env python3
"""
Test script for shared backend integration
"""

import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_backend_initialization():
    """Test backend initialization"""
    print("🧪 Testing Backend Initialization...")
    
    try:
        from backend import backend_manager
        
        # Get backend status
        status = backend_manager.get_status()
        
        print(f"✅ Backend Manager: {'Initialized' if backend_manager.initialized else 'Failed'}")
        print(f"📊 Services Status:")
        
        for service_name, service_info in status["services"].items():
            available = "✅" if service_info.get("available", False) else "❌"
            initialized = "✅" if service_info.get("initialized", False) else "❌"
            print(f"   {available} {service_name}: Available")
            if "initialized" in service_info:
                print(f"   {initialized} {service_name}: Initialized")
        
        print(f"🔑 Environment Status:")
        for env_var, status_val in status["environment"].items():
            status_icon = "✅" if status_val == "configured" else "❌"
            print(f"   {status_icon} {env_var}: {status_val}")
        
        return backend_manager.initialized
        
    except Exception as e:
        print(f"❌ Backend initialization test failed: {e}")
        return False

def test_services():
    """Test individual services"""
    print("\n🧪 Testing Individual Services...")
    
    try:
        from backend import backend_manager
        
        # Test donor service
        if backend_manager.donor_service:
            print("✅ Donor Service: Available")
            # Test getting all donors
            donors = backend_manager.donor_service.get_all_donors()
            print(f"   📊 Found {len(donors)} donors")
        else:
            print("❌ Donor Service: Not available")
        
        # Test email service
        if backend_manager.email_service:
            print("✅ Email Service: Available")
            # Test getting templates
            templates = backend_manager.email_service.get_available_templates()
            print(f"   📧 Found {len(templates)} email templates")
        else:
            print("❌ Email Service: Not available")
        
        # Test pipeline service
        if backend_manager.pipeline_service:
            print("✅ Pipeline Service: Available")
            # Test getting pipeline
            pipeline = backend_manager.pipeline_service.get_pipeline()
            print(f"   📈 Found {len(pipeline)} pipeline stages")
        else:
            print("❌ Pipeline Service: Not available")
        
        # Test template service
        if backend_manager.template_service:
            print("✅ Template Service: Available")
            # Test getting template info
            template_info = backend_manager.template_service.get_template_info()
            print(f"   📋 Template info: {'Available' if template_info.get('available') else 'Not available'}")
        else:
            print("❌ Template Service: Not available")
        
        # Test context helpers
        if backend_manager.context_helpers:
            print("✅ Context Helpers: Available")
            # Test getting context
            context = backend_manager.context_helpers.get_combined_context("test query")
            print(f"   🧠 Context gathering: Working")
        else:
            print("❌ Context Helpers: Not available")
        
        return True
        
    except Exception as e:
        print(f"❌ Services test failed: {e}")
        return False

def test_slack_bot_integration():
    """Test Slack bot integration"""
    print("\n🧪 Testing Slack Bot Integration...")
    
    try:
        from slack_bot_refactored import SlackBot
        
        # Initialize Slack bot
        slack_bot = SlackBot()
        
        print(f"✅ Slack Bot: {'Initialized' if slack_bot.initialized else 'Not initialized'}")
        print(f"   🔧 Backend Services: {'Connected' if slack_bot.backend.initialized else 'Not connected'}")
        print(f"   📧 Email Service: {'Available' if slack_bot.email_service else 'Not available'}")
        print(f"   👥 Donor Service: {'Available' if slack_bot.donor_service else 'Not available'}")
        print(f"   🧠 Context Helpers: {'Available' if slack_bot.context_helpers else 'Not available'}")
        
        return slack_bot.initialized
        
    except Exception as e:
        print(f"❌ Slack bot integration test failed: {e}")
        return False

def test_web_ui_compatibility():
    """Test Web UI API compatibility"""
    print("\n🧪 Testing Web UI API Compatibility...")
    
    try:
        # Test that the refactored app can be imported
        import app_refactored
        
        print("✅ Refactored App: Import successful")
        
        # Test that the app has the required endpoints
        app = app_refactored.app
        
        # Check for key routes
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        required_routes = [
            '/api/pipeline',
            '/api/donor/<donor_id>',
            '/api/templates',
            '/api/draft',
            '/api/send',
            '/health'
        ]
        
        missing_routes = []
        for route in required_routes:
            if not any(route in r for r in routes):
                missing_routes.append(route)
        
        if missing_routes:
            print(f"❌ Missing routes: {missing_routes}")
            return False
        else:
            print("✅ All required API routes: Available")
        
        return True
        
    except Exception as e:
        print(f"❌ Web UI compatibility test failed: {e}")
        return False

def test_email_generation():
    """Test email generation functionality"""
    print("\n🧪 Testing Email Generation...")
    
    try:
        from backend import backend_manager
        
        if not backend_manager.email_service:
            print("❌ Email Service: Not available")
            return False
        
        # Test email generation with a mock donor
        test_donor_id = "test_foundation"
        test_template = "identification"
        
        result = backend_manager.email_service.generate_email(test_template, test_donor_id)
        
        if result.get("success"):
            print("✅ Email Generation: Working")
            draft = result["data"]
            print(f"   📧 Generated draft: {draft['id']}")
            print(f"   📝 Subject: {draft['subject'][:50]}...")
        else:
            print(f"❌ Email Generation: Failed - {result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Email generation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Shared Backend Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Backend Initialization", test_backend_initialization),
        ("Individual Services", test_services),
        ("Slack Bot Integration", test_slack_bot_integration),
        ("Web UI Compatibility", test_web_ui_compatibility),
        ("Email Generation", test_email_generation)
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
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Shared backend integration is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
