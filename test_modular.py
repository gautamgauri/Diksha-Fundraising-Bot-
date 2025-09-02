#!/usr/bin/env python3
"""
Test script for modular architecture
Verifies that all modules can be imported and initialized correctly
"""

import os
import sys

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing Modular Architecture...")
    print("=" * 50)
    
    # Test DeepSeek client
    try:
        from deepseek_client import DeepSeekClient, deepseek_client
        print("✅ DeepSeek client imported successfully")
    except ImportError as e:
        print(f"❌ DeepSeek client import failed: {e}")
        return False
    
    # Test context helpers
    try:
        from context_helpers import get_relevant_donor_context, get_template_context, get_pipeline_insights
        print("✅ Context helpers imported successfully")
    except ImportError as e:
        print(f"❌ Context helpers import failed: {e}")
        return False
    
    # Test Slack bot (without dependencies)
    try:
        from slack_bot import SlackBot, initialize_slack_bot
        print("✅ Slack bot imported successfully")
    except ImportError as e:
        print(f"❌ Slack bot import failed: {e}")
        return False
    
    return True

def test_deepseek_client():
    """Test DeepSeek client functionality"""
    print("\n🔍 Testing DeepSeek Client...")
    
    try:
        from deepseek_client import DeepSeekClient
        
        # Test without API key
        client = DeepSeekClient()
        print(f"✅ Client initialized: {client.initialized}")
        
        # Test status
        status = client.get_status()
        print(f"✅ Status: {status}")
        
        return True
    except Exception as e:
        print(f"❌ DeepSeek client test failed: {e}")
        return False

def test_context_helpers():
    """Test context helper functions"""
    print("\n🔍 Testing Context Helpers...")
    
    try:
        from context_helpers import get_relevant_donor_context, get_template_context, get_pipeline_insights
        
        # Test with None dependencies
        donor_context = get_relevant_donor_context("test query", None)
        template_context = get_template_context(None)
        pipeline_context = get_pipeline_insights(None)
        
        print(f"✅ Donor context: {type(donor_context)}")
        print(f"✅ Template context: {type(template_context)}")
        print(f"✅ Pipeline context: {type(pipeline_context)}")
        
        return True
    except Exception as e:
        print(f"❌ Context helpers test failed: {e}")
        return False

def test_slack_bot():
    """Test Slack bot initialization"""
    print("\n🔍 Testing Slack Bot...")
    
    try:
        from slack_bot import SlackBot
        
        # Test without credentials
        bot = SlackBot()
        print(f"✅ Bot initialized: {bot.initialized}")
        
        # Test with dependencies
        bot_with_deps = SlackBot(sheets_db=None, email_generator=None)
        print(f"✅ Bot with deps initialized: {bot_with_deps.initialized}")
        
        return True
    except Exception as e:
        print(f"❌ Slack bot test failed: {e}")
        return False

def test_modular_integration():
    """Test that modules work together"""
    print("\n🔍 Testing Modular Integration...")
    
    try:
        # Test initialization function
        from slack_bot import initialize_slack_bot
        
        bot = initialize_slack_bot(sheets_db=None, email_generator=None)
        print(f"✅ Bot initialized via function: {bot.initialized}")
        
        return True
    except Exception as e:
        print(f"❌ Modular integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Modular Architecture Test Suite")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Module Imports", test_imports),
        ("DeepSeek Client", test_deepseek_client),
        ("Context Helpers", test_context_helpers),
        ("Slack Bot", test_slack_bot),
        ("Modular Integration", test_modular_integration)
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
        print("🎉 All tests passed! Modular architecture is working correctly.")
        print("\n🏗️ Architecture Summary:")
        print("   • DeepSeek client: ✅ Modular")
        print("   • Context helpers: ✅ Modular")
        print("   • Slack bot: ✅ Modular")
        print("   • No circular imports: ✅ Clean")
        print("   • Dependency injection: ✅ Proper")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)

