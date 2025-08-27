#!/usr/bin/env python3
"""
Test script for Google Sheets integration
Run this to verify the connection and basic functionality
"""

import os
import sys
from app import sheets_manager, SHEET_NAME

def test_sheets_connection():
    """Test the Google Sheets connection"""
    print("🔍 Testing Google Sheets Integration...")
    print(f"📊 Target Sheet: {SHEET_NAME}")
    print()
    
    # Check if credentials file exists
    creds_file = "dikshaindia-172709-21ff58e7e4d4.json"
    if not os.path.exists(creds_file):
        print(f"❌ Credentials file not found: {creds_file}")
        return False
    
    print(f"✅ Credentials file found: {creds_file}")
    
    # Check connection
    if not sheets_manager.initialized:
        print("❌ Google Sheets connection failed")
        return False
    
    print("✅ Google Sheets connected successfully")
    
    # Test getting sample data
    try:
        org_names = sheets_manager.sheet.col_values(1)[1:6]  # First 5 organizations
        print(f"📋 Sample organizations: {org_names}")
        print(f"📊 Total organizations: {len(sheets_manager.sheet.col_values(1)) - 1}")
        
        # Test search functionality
        if org_names:
            test_org = org_names[0]
            print(f"\n🔍 Testing search for: {test_org}")
            matches = sheets_manager.search_organizations(test_org[:5])  # First 5 chars
            print(f"   Found matches: {matches}")
            
            # Test getting organization data
            print(f"\n📋 Testing get_organization_data for: {test_org}")
            org_data = sheets_manager.get_organization_data(test_org)
            if org_data:
                print(f"   ✅ Found data: {org_data}")
            else:
                print(f"   ❌ No data found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing functionality: {e}")
        return False

if __name__ == "__main__":
    success = test_sheets_connection()
    if success:
        print("\n🎉 All tests passed! Google Sheets integration is working.")
    else:
        print("\n💥 Tests failed. Check your setup.")
        sys.exit(1)

