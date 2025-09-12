#!/usr/bin/env python3
"""
Railway Deployment Debug Script
Run this on Railway to diagnose deployment issues
"""

import os
import sys
import json
import base64
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🚂 {title}")
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

def test_railway_environment():
    """Test Railway-specific environment"""
    print_header("Railway Environment Check")
    
    # Check Railway environment variables
    railway_vars = [
        'PORT',
        'RAILWAY_PUBLIC_DOMAIN',
        'RAILWAY_ENVIRONMENT',
        'RAILWAY_PROJECT_ID'
    ]
    
    for var in railway_vars:
        value = os.getenv(var)
        if value:
            print_success(f"{var}: {value}")
        else:
            print_warning(f"{var}: Not set")
    
    # Check if we're running on Railway
    if os.getenv('RAILWAY_ENVIRONMENT'):
        print_success("Running on Railway platform")
    else:
        print_warning("Not running on Railway (local development?)")
    
    return True

def test_port_configuration():
    """Test port configuration"""
    print_header("Port Configuration Check")
    
    port = os.getenv('PORT')
    if port:
        try:
            port_int = int(port)
            print_success(f"PORT environment variable: {port_int}")
            return True
        except ValueError:
            print_error(f"PORT is not a valid integer: {port}")
            return False
    else:
        print_error("PORT environment variable not set")
        return False

def test_google_sheets_railway():
    """Test Google Sheets configuration on Railway"""
    print_header("Google Sheets Railway Check")
    
    # Check sheet ID
    sheet_id = os.getenv('MAIN_SHEET_ID')
    if sheet_id:
        print_success(f"MAIN_SHEET_ID: {sheet_id}")
    else:
        print_error("MAIN_SHEET_ID not set")
        return False
    
    # Check credentials
    credentials_b64 = os.getenv('GOOGLE_CREDENTIALS_BASE64')
    if credentials_b64:
        try:
            credentials_json = base64.b64decode(credentials_b64).decode('utf-8')
            credentials_info = json.loads(credentials_json)
            print_success("GOOGLE_CREDENTIALS_BASE64 decoded successfully")
            print_info(f"Service account: {credentials_info.get('client_email', 'Unknown')}")
            return True
        except Exception as e:
            print_error(f"GOOGLE_CREDENTIALS_BASE64 decode failed: {e}")
            return False
    else:
        print_error("GOOGLE_CREDENTIALS_BASE64 not set")
        return False

def test_flask_startup():
    """Test Flask app startup on Railway"""
    print_header("Flask Startup Check")
    
    try:
        # Import Flask app
        from app import app
        print_success("Flask app imported successfully")
        
        # Check if app has required routes
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        required_routes = ['/', '/api/health']
        
        for route in required_routes:
            if route in routes:
                print_success(f"Route {route} exists")
            else:
                print_error(f"Route {route} missing")
        
        return True
        
    except Exception as e:
        print_error(f"Flask app import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_railway():
    """Test backend on Railway"""
    print_header("Backend Railway Check")
    
    try:
        from backend import backend_manager
        print_success("Backend imported successfully")
        
        if backend_manager:
            print_success("Backend manager available")
            
            # Test SheetsDB specifically
            if hasattr(backend_manager, 'sheets_db'):
                sheets_db = backend_manager.sheets_db
                if sheets_db and sheets_db.initialized:
                    print_success("SheetsDB initialized successfully")
                    
                    # Test a simple data retrieval
                    try:
                        data = sheets_db.get_pipeline_data()
                        print_success(f"Pipeline data retrieved: {len(data)} records")
                        return True
                    except Exception as e:
                        print_error(f"Pipeline data retrieval failed: {e}")
                        return False
                else:
                    print_error("SheetsDB not initialized")
                    return False
            else:
                print_error("SheetsDB not found in backend manager")
                return False
        else:
            print_error("Backend manager is None")
            return False
            
    except Exception as e:
        print_error(f"Backend test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_health_check():
    """Test health check endpoint"""
    print_header("Health Check Test")
    
    try:
        from app import app
        
        # Create a test client
        with app.test_client() as client:
            response = client.get('/api/health')
            
            if response.status_code == 200:
                print_success(f"Health check passed: {response.status_code}")
                
                # Check response content
                try:
                    data = response.get_json()
                    print_success(f"Health check response: {data}")
                    return True
                except Exception as e:
                    print_warning(f"Health check response parsing failed: {e}")
                    return True  # Still consider it a success if status is 200
            else:
                print_error(f"Health check failed: {response.status_code}")
                return False
                
    except Exception as e:
        print_error(f"Health check test failed: {e}")
        return False

def test_api_endpoints_railway():
    """Test API endpoints on Railway"""
    print_header("API Endpoints Railway Test")
    
    try:
        from app import app
        
        endpoints = [
            ('/', 'Root endpoint'),
            ('/api/health', 'Health check'),
            ('/api/pipeline', 'Pipeline data'),
            ('/api/activities', 'Activities data'),
            ('/api/proposals', 'Proposals data'),
            ('/api/alerts', 'Alerts data')
        ]
        
        with app.test_client() as client:
            for endpoint, description in endpoints:
                try:
                    response = client.get(endpoint)
                    if response.status_code == 200:
                        print_success(f"{endpoint}: {response.status_code} - {description}")
                    else:
                        print_warning(f"{endpoint}: {response.status_code} - {description}")
                except Exception as e:
                    print_error(f"{endpoint}: {e} - {description}")
        
        return True
        
    except Exception as e:
        print_error(f"API endpoints test failed: {e}")
        return False

def main():
    """Main Railway debug function"""
    print_header("Railway Deployment Debug")
    print_info(f"Debug started at: {datetime.now().isoformat()}")
    print_info(f"Python version: {sys.version}")
    print_info(f"Working directory: {os.getcwd()}")
    
    tests = [
        ("Railway Environment", test_railway_environment),
        ("Port Configuration", test_port_configuration),
        ("Google Sheets Railway", test_google_sheets_railway),
        ("Flask Startup", test_flask_startup),
        ("Backend Railway", test_backend_railway),
        ("Health Check", test_health_check),
        ("API Endpoints Railway", test_api_endpoints_railway)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print_error(f"{test_name} test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print_header("Railway Debug Summary")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print_info(f"Tests passed: {passed}/{total}")
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    if passed == total:
        print_success("All Railway tests passed! Deployment should work.")
    else:
        print_warning(f"{total - passed} tests failed. Check Railway configuration.")
    
    # Railway-specific recommendations
    print_header("Railway Recommendations")
    
    if not results.get("Port Configuration", False):
        print_info("Set PORT environment variable in Railway dashboard")
    
    if not results.get("Google Sheets Railway", False):
        print_info("Set MAIN_SHEET_ID and GOOGLE_CREDENTIALS_BASE64 in Railway")
    
    if not results.get("Health Check", False):
        print_info("Check Railway health check configuration")
    
    print_info(f"Debug completed at: {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
