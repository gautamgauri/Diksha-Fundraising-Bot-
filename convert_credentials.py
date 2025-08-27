#!/usr/bin/env python3
"""
Script to convert Google service account JSON credentials to base64
for use as an environment variable
"""

import base64
import json
import os

def convert_credentials_to_base64():
    """Convert Google credentials JSON file to base64"""
    
    # Check if credentials file exists
    creds_file = "dikshaindia-172709-21ff58e7e4d4.json"
    if not os.path.exists(creds_file):
        print(f"❌ Credentials file not found: {creds_file}")
        print("💡 Make sure the Google service account JSON file is in the project root")
        return
    
    try:
        # Read the JSON file
        with open(creds_file, 'r') as f:
            credentials_json = f.read()
        
        # Validate JSON
        json.loads(credentials_json)
        
        # Convert to base64
        credentials_base64 = base64.b64encode(credentials_json.encode('utf-8')).decode('utf-8')
        
        print("✅ Successfully converted credentials to base64")
        print("\n📋 Add this to your environment variables:")
        print(f"GOOGLE_CREDENTIALS_BASE64={credentials_base64}")
        
        print("\n🔧 For Railway deployment:")
        print("1. Go to your Railway project")
        print("2. Navigate to Variables tab")
        print("3. Add the GOOGLE_CREDENTIALS_BASE64 variable with the value above")
        
        print("\n🔧 For local development:")
        print("1. Create a .env file in the project root")
        print("2. Add: GOOGLE_CREDENTIALS_BASE64=your_base64_string_here")
        
        return credentials_base64
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in credentials file: {e}")
    except Exception as e:
        print(f"❌ Error converting credentials: {e}")

if __name__ == "__main__":
    convert_credentials_to_base64()

