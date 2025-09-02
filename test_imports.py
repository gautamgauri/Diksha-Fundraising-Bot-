#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
Run this before deploying to Railway
"""

import sys
import os

def test_imports():
    """Test all required imports"""
    print("🧪 Testing imports...")
    
    # Test basic Python imports
    try:
        import logging
        print("✅ logging")
    except ImportError as e:
        print(f"❌ logging: {e}")
        return False
    
    try:
        import json
        print("✅ json")
    except ImportError as e:
        print(f"❌ json: {e}")
        return False
    
    # Test Flask
    try:
        from flask import Flask
        print("✅ Flask")
    except ImportError as e:
        print(f"❌ Flask: {e}")
        return False
    
    # Test Google APIs
    try:
        from google.oauth2 import service_account
        print("✅ google.oauth2.service_account")
    except ImportError as e:
        print(f"❌ google.oauth2.service_account: {e}")
        return False
    
    try:
        from googleapiclient.discovery import build
        print("✅ googleapiclient.discovery")
    except ImportError as e:
        print(f"❌ googleapiclient.discovery: {e}")
        return False
    
    # Test Slack
    try:
        from slack_bolt import App
        print("✅ slack_bolt")
    except ImportError as e:
        print(f"❌ slack_bolt: {e}")
        return False
    
    # Test AI
    try:
        import anthropic
        print("✅ anthropic")
    except ImportError as e:
        print(f"❌ anthropic: {e}")
        return False
    
    # Test data processing
    try:
        import pandas
        print("✅ pandas")
    except ImportError as e:
        print(f"❌ pandas: {e}")
        return False
    
    try:
        import numpy
        print("✅ numpy")
    except ImportError as e:
        print(f"❌ numpy: {e}")
        return False
    
    # Test fuzzy matching
    try:
        from fuzzywuzzy import fuzz
        print("✅ fuzzywuzzy")
    except ImportError as e:
        print(f"❌ fuzzywuzzy: {e}")
        return False
    
    # Test custom modules
    try:
        from sheets_sync import SheetsDB
        print("✅ sheets_sync")
    except ImportError as e:
        print(f"❌ sheets_sync: {e}")
        return False
    
    try:
        from email_generator import EmailGenerator
        print("✅ email_generator")
    except ImportError as e:
        print(f"❌ email_generator: {e}")
        return False
    
    try:
        from cache_manager import cache_manager
        print("✅ cache_manager")
    except ImportError as e:
        print(f"❌ cache_manager: {e}")
        return False
    
    print("\n🎉 All imports successful!")
    return True

def test_basic_functionality():
    """Test basic functionality without external services"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test Flask app creation
        from flask import Flask
        app = Flask(__name__)
        print("✅ Flask app creation")
        
        # Test basic route
        @app.route('/test')
        def test():
            return 'OK'
        
        print("✅ Route definition")
        
        # Test app context
        with app.test_client() as client:
            response = client.get('/test')
            if response.status_code == 200:
                print("✅ Route execution")
            else:
                print(f"❌ Route execution: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Diksha Foundation Fundraising Bot - Import Test")
    print("=" * 60)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed!")
        sys.exit(1)
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Basic functionality test failed!")
        sys.exit(1)
    
    print("\n🎉 All tests passed! Ready for Railway deployment!")
    print("=" * 60)
