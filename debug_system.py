#!/usr/bin/env python3
"""
Diksha Fundraising Bot - System Debug Script
Run this script to diagnose common issues
"""

import sys
import os
import json
import base64
import time
import requests
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def test_python_environment():
    """Test Python environment"""
    print_header("Python Environment Check")
    
    print_info(f"Python version: {sys.version}")
    print_info(f"Python executable: {sys.executable}")
    print_info(f"Current working directory: {os.getcwd()}")
    
    # Check if we're in the right directory
    if os.path.exists('app.py'):
        print_success("Found app.py in current directory")
    else:
        print_error("app.py not found in current directory")
        return False
    
    return True

def test_dependencies():
    """Test if all dependencies are installed"""
    print_header("Dependencies Check")
    
    required_packages = [
        'flask', 'requests', 'pandas', 'google.auth', 
        'googleapiclient', 'streamlit'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('.', '_'))
            print_success(f"{package} is installed")
        except ImportError:
            print_error(f"{package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print_warning(f"Missing packages: {', '.join(missing_packages)}")
        print_info("Run: pip install -r requirements.txt")
        return False
    
    return True

def test_environment_variables():
    """Test environment variables"""
    print_header("Environment Variables Check")
    
    required_vars = [
        'MAIN_SHEET_ID',
        'GOOGLE_CREDENTIALS_BASE64'
    ]
    
    optional_vars = [
        'PORT',
        'API_BASE',
        'ALLOWED_USERS'
    ]
    
    all_good = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print_success(f"{var} is set")
            if var == 'GOOGLE_CREDENTIALS_BASE64':
                try:
                    # Test if credentials can be decoded
                    decoded = base64.b64decode(value).decode('utf-8')
                    creds = json.loads(decoded)
                    print_success(f"Credentials decoded successfully")
                    print_info(f"Service account: {creds.get('client_email', 'Unknown')}")
                except Exception as e:
                    print_error(f"Credentials decode failed: {e}")
                    all_good = False
        else:
            print_error(f"{var} is not set")
            all_good = False
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print_success(f"{var} is set: {value}")
        else:
            print_warning(f"{var} is not set (optional)")
    
    return all_good

def test_flask_app():
    """Test Flask app import and basic functionality"""
    print_header("Flask App Check")
    
    try:
        from app import app
        print_success("Flask app imported successfully")
        
        # Test if app has required routes
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        required_routes = ['/', '/api/health', '/api/pipeline']
        
        for route in required_routes:
            if route in routes:
                print_success(f"Route {route} exists")
            else:
                print_error(f"Route {route} missing")
        
        return True
        
    except Exception as e:
        print_error(f"Flask app import failed: {e}")
        return False

def test_backend_imports():
    """Test backend imports"""
    print_header("Backend Imports Check")
    
    try:
        from backend import backend_manager
        print_success("Backend package imported successfully")
        
        if backend_manager:
            print_success("Backend manager is available")
            
            # Test individual services
            services = [
                'donor_service', 'email_service', 'pipeline_service',
                'template_service', 'context_helpers', 'deepseek_client', 'sheets_db'
            ]
            
            for service in services:
                if hasattr(backend_manager, service):
                    service_obj = getattr(backend_manager, service)
                    if service_obj:
                        print_success(f"{service} is available")
                    else:
                        print_warning(f"{service} is None")
                else:
                    print_error(f"{service} not found")
        else:
            print_warning("Backend manager is None")
        
        return True
        
    except Exception as e:
        print_error(f"Backend import failed: {e}")
        return False

def test_google_sheets():
    """Test Google Sheets connectivity"""
    print_header("Google Sheets Check")
    
    try:
        from backend.core.sheets_db import SheetsDB
        
        sheets_db = SheetsDB()
        if sheets_db.initialized:
            print_success("SheetsDB initialized successfully")
            
            # Test data retrieval
            try:
                pipeline_data = sheets_db.get_pipeline_data()
                print_success(f"Pipeline data: {len(pipeline_data)} records")
            except Exception as e:
                print_error(f"Pipeline data retrieval failed: {e}")
            
            try:
                activities = sheets_db.get_interaction_log()
                print_success(f"Activities: {len(activities)} records")
            except Exception as e:
                print_error(f"Activities retrieval failed: {e}")
            
            try:
                proposals = sheets_db.get_proposals()
                print_success(f"Proposals: {len(proposals)} records")
            except Exception as e:
                print_error(f"Proposals retrieval failed: {e}")
            
            try:
                alerts = sheets_db.get_alerts()
                print_success(f"Alerts: {len(alerts)} records")
            except Exception as e:
                print_error(f"Alerts retrieval failed: {e}")
            
            return True
        else:
            print_error("SheetsDB initialization failed")
            return False
            
    except Exception as e:
        print_error(f"Google Sheets test failed: {e}")
        return False

def test_streamlit_imports():
    """Test Streamlit app imports"""
    print_header("Streamlit Imports Check")
    
    # Check if streamlit-app directory exists
    if not os.path.exists('streamlit-app'):
        print_error("streamlit-app directory not found")
        return False
    
    print_success("streamlit-app directory found")
    
    # Check lib directory
    lib_path = os.path.join('streamlit-app', 'lib')
    if os.path.exists(lib_path):
        print_success("streamlit-app/lib directory found")
        
        # Check required files
        required_files = ['__init__.py', 'api.py', 'auth.py']
        for file in required_files:
            file_path = os.path.join(lib_path, file)
            if os.path.exists(file_path):
                print_success(f"{file} exists")
            else:
                print_error(f"{file} missing")
    else:
        print_error("streamlit-app/lib directory not found")
        return False
    
    return True

def test_api_endpoints():
    """Test API endpoints (if Flask app is running)"""
    print_header("API Endpoints Check")
    
    base_url = "http://localhost:5000"
    endpoints = [
        '/',
        '/api/health',
        '/api/pipeline',
        '/api/activities',
        '/api/proposals',
        '/api/alerts'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print_success(f"{endpoint}: {response.status_code}")
            else:
                print_warning(f"{endpoint}: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print_warning(f"{endpoint}: Connection failed (Flask app not running?)")
        except Exception as e:
            print_error(f"{endpoint}: {e}")

def main():
    """Main debug function"""
    print_header("Diksha Fundraising Bot - System Debug")
    print_info(f"Debug started at: {datetime.now().isoformat()}")
    
    tests = [
        ("Python Environment", test_python_environment),
        ("Dependencies", test_dependencies),
        ("Environment Variables", test_environment_variables),
        ("Flask App", test_flask_app),
        ("Backend Imports", test_backend_imports),
        ("Google Sheets", test_google_sheets),
        ("Streamlit Imports", test_streamlit_imports),
        ("API Endpoints", test_api_endpoints)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print_error(f"{test_name} test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print_header("Debug Summary")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print_info(f"Tests passed: {passed}/{total}")
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    if passed == total:
        print_success("All tests passed! System is ready.")
    else:
        print_warning(f"{total - passed} tests failed. Check the issues above.")
    
    print_info(f"Debug completed at: {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
