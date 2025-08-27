#!/usr/bin/env python3
"""
Debug script to check Google Sheets access
"""

import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def debug_sheets_access():
    """Debug Google Sheets access"""
    print("🔍 Debugging Google Sheets Access...")
    
    # Check credentials file
    creds_file = "dikshaindia-172709-21ff58e7e4d4.json"
    if not os.path.exists(creds_file):
        print(f"❌ Credentials file not found: {creds_file}")
        return
    
    print(f"✅ Credentials file found: {creds_file}")
    
    try:
        # Authenticate
        credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_file, SCOPES)
        client = gspread.authorize(credentials)
        print("✅ Authentication successful")
        
        # List available spreadsheets
        print("\n📋 Available spreadsheets:")
        try:
            spreadsheets = client.openall()
            for i, sheet in enumerate(spreadsheets[:10]):  # Show first 10
                print(f"  {i+1}. {sheet.title}")
            
            if len(spreadsheets) > 10:
                print(f"  ... and {len(spreadsheets) - 10} more")
                
        except Exception as e:
            print(f"❌ Error listing spreadsheets: {e}")
        
        # Try to open the specific sheet
        target_sheet = "Diksha_Donor_Pipeline_2025_v2"
        print(f"\n🎯 Trying to open: {target_sheet}")
        
        try:
            sheet = client.open(target_sheet)
            print(f"✅ Successfully opened: {sheet.title}")
            
            # Check the first worksheet
            worksheet = sheet.sheet1
            print(f"📊 Worksheet: {worksheet.title}")
            
            # Get some sample data
            try:
                headers = worksheet.row_values(1)
                print(f"📋 Headers: {headers}")
                
                # Get first few rows
                sample_data = worksheet.get_all_values()[:5]
                print(f"📄 Sample data (first 5 rows):")
                for i, row in enumerate(sample_data):
                    print(f"  Row {i+1}: {row}")
                    
            except Exception as e:
                print(f"❌ Error reading data: {e}")
                
        except gspread.SpreadsheetNotFound:
            print(f"❌ Spreadsheet '{target_sheet}' not found")
            print("💡 Make sure the service account has access to this spreadsheet")
            
        except Exception as e:
            print(f"❌ Error opening spreadsheet: {e}")
            
    except Exception as e:
        print(f"❌ Authentication failed: {e}")

if __name__ == "__main__":
    debug_sheets_access()

