"""
Google Authentication Module
Handles Google API authentication using base64 encoded service account credentials
"""

import os
import base64
import json
import logging
from typing import Tuple, Optional
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Disable discovery cache warnings
import warnings
warnings.filterwarnings("ignore", message="file_cache is only supported with oauth2client<4.0.0")

logger = logging.getLogger(__name__)

# Google API scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def decode_credentials() -> Optional[dict]:
    """
    Decode base64 encoded service account JSON from environment variable
    
    Returns:
        dict: Decoded service account credentials or None if failed
    """
    try:
        # Get base64 encoded credentials from environment
        credentials_base64 = os.environ.get('GOOGLE_CREDENTIALS_BASE64')
        if not credentials_base64:
            logger.error("❌ GOOGLE_CREDENTIALS_BASE64 environment variable not set")
            return None
        
        # Decode base64 to JSON
        credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
        credentials_dict = json.loads(credentials_json)
        
        logger.info("✅ Successfully decoded Google credentials")
        return credentials_dict
        
    except Exception as e:
        logger.error(f"❌ Failed to decode Google credentials: {e}")
        return None

def create_google_clients() -> Tuple[Optional[object], Optional[object]]:
    """
    Create Google Sheets and Drive API clients
    
    Returns:
        Tuple[sheets_client, drive_client]: Google API clients or (None, None) if failed
    """
    try:
        # Decode credentials
        credentials_dict = decode_credentials()
        if not credentials_dict:
            return None, None
        
        # Create credentials object
        credentials = Credentials.from_service_account_info(
            credentials_dict, 
            scopes=SCOPES
        )
        
        # Build API clients
        sheets_service = build('sheets', 'v4', credentials=credentials)
        drive_service = build('drive', 'v3', credentials=credentials)
        
        logger.info("✅ Successfully created Google API clients")
        return sheets_service, drive_service
        
    except HttpError as e:
        logger.error(f"❌ Google API HTTP error: {e}")
        return None, None
    except Exception as e:
        logger.error(f"❌ Failed to create Google API clients: {e}")
        return None, None

def test_connection() -> bool:
    """
    Test Google API connection
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        sheets_service, drive_service = create_google_clients()
        if not sheets_service or not drive_service:
            return False
        
        # Test Sheets API by making a simple request
        # This will fail if credentials are invalid
        sheets_service.spreadsheets().get(spreadsheetId='test').execute()
        
    except HttpError as e:
        if e.resp.status == 404:
            # 404 is expected for a test ID, but it means the API is working
            logger.info("✅ Google Sheets API connection test successful")
            return True
        else:
            logger.error(f"❌ Google Sheets API test failed: {e}")
            return False
    except Exception as e:
        logger.error(f"❌ Google API connection test failed: {e}")
        return False
    
    return True
