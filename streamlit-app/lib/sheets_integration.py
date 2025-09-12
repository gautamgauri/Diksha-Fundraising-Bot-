"""
Google Sheets Integration for Streamlit App
Self-contained Google Sheets access for Railway deployment
"""

import os
import logging
from typing import Dict, List, Optional, Any

# Try to import Google API dependencies with fallback
try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Google API dependencies not available: {e}")
    GOOGLE_API_AVAILABLE = False
    # Create mock classes for fallback
    class HttpError(Exception):
        pass
    class Credentials:
        pass
    class build:
        pass

logger = logging.getLogger(__name__)

class SheetsIntegration:
    """Self-contained Google Sheets integration for Streamlit app"""
    
    def __init__(self):
        self.initialized = False
        self.sheets_service = None
        self.sheet_id = None
        
        if GOOGLE_API_AVAILABLE:
            self._initialize()
    
    def _initialize(self):
        """Initialize Google Sheets connection"""
        try:
            # Get configuration from environment variables
            self.sheet_id = os.getenv("MAIN_SHEET_ID")
            credentials_base64 = os.getenv("GOOGLE_CREDENTIALS_BASE64")
            
            if not self.sheet_id or not credentials_base64:
                logger.warning("⚠️ Missing Google Sheets configuration")
                return
            
            # Decode credentials
            import base64
            import json
            
            credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
            credentials_info = json.loads(credentials_json)
            
            # Create credentials
            scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
            creds = Credentials.from_service_account_info(credentials_info, scopes=scopes)
            
            # Build service
            self.sheets_service = build('sheets', 'v4', credentials=creds)
            self.initialized = True
            
            logger.info("✅ Google Sheets integration initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Sheets: {e}")
            self.initialized = False
    
    def get_pipeline_data(self) -> List[Dict[str, Any]]:
        """Get pipeline data from Google Sheets"""
        if not self.initialized:
            logger.error("❌ SheetsIntegration not initialized")
            return []
        
        try:
            # Read data from the main sheet (Pipeline Tracker tab)
            range_name = "Pipeline Tracker!A:Z"
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                logger.warning("⚠️ No data found in Pipeline Tracker tab")
                return []
            
            # Skip header row
            data_rows = values[1:]
            
            # Convert to list of dictionaries
            pipeline_data = []
            headers = values[0] if values else []
            
            for row in data_rows:
                # Skip empty rows
                if not any(cell.strip() for cell in row if cell):
                    continue
                
                # Create donor dictionary
                donor = {}
                for i, header in enumerate(headers):
                    donor[header] = row[i] if i < len(row) else ""
                
                pipeline_data.append(donor)
            
            logger.info(f"✅ Retrieved {len(pipeline_data)} pipeline entries")
            return pipeline_data
            
        except HttpError as e:
            logger.error(f"❌ HTTP error getting pipeline data: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error getting pipeline data: {e}")
            return []
    
    def get_interaction_log(self) -> List[Dict[str, Any]]:
        """Get interaction log data from Google Sheets"""
        if not self.initialized:
            logger.error("❌ SheetsIntegration not initialized")
            return []
        
        try:
            # Read data from the Interaction Log tab
            range_name = "Interaction Log!A:H"
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                logger.warning("⚠️ No data found in Interaction Log tab")
                return []
            
            # Skip header row
            data_rows = values[1:]
            
            # Convert to list of dictionaries
            interactions = []
            headers = ['Date', 'Organization Name', 'Interaction Type', 'Team Member', 'Summary/Notes', 'Next Steps', 'Follow-up Date', 'Attachments']
            
            for row in data_rows:
                # Skip empty rows
                if not any(cell.strip() for cell in row if cell):
                    continue
                
                # Create interaction dictionary
                interaction = {}
                for i, header in enumerate(headers):
                    interaction[header] = row[i] if i < len(row) else ""
                
                interactions.append(interaction)
            
            logger.info(f"✅ Retrieved {len(interactions)} interaction log entries")
            return interactions
            
        except HttpError as e:
            logger.error(f"❌ HTTP error getting interaction log: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error getting interaction log: {e}")
            return []
    
    def get_proposals(self) -> List[Dict[str, Any]]:
        """Get proposals data from Google Sheets"""
        if not self.initialized:
            logger.error("❌ SheetsIntegration not initialized")
            return []
        
        try:
            # Read data from the Proposals Tracker tab
            range_name = "Proposals Tracker!A:H"
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                logger.warning("⚠️ No data found in Proposals Tracker tab")
                return []
            
            # Skip header row
            data_rows = values[1:]
            
            # Convert to list of dictionaries
            proposals = []
            headers = ['Organization Name', 'Proposal Title', 'Amount Requested', 'Submission Date', 'Decision Deadline', 'Status', 'Assigned Writer', 'Final Amount']
            
            for row in data_rows:
                # Skip empty rows
                if not any(cell.strip() for cell in row if cell):
                    continue
                
                # Create proposal dictionary
                proposal = {}
                for i, header in enumerate(headers):
                    proposal[header] = row[i] if i < len(row) else ""
                
                proposals.append(proposal)
            
            logger.info(f"✅ Retrieved {len(proposals)} proposals")
            return proposals
            
        except HttpError as e:
            logger.error(f"❌ HTTP error getting proposals: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error getting proposals: {e}")
            return []
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get alerts data from Google Sheets"""
        if not self.initialized:
            logger.error("❌ SheetsIntegration not initialized")
            return []
        
        try:
            # Read data from the Deadline Alerts Log tab
            range_name = "Deadline Alerts Log!A:G"
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                logger.warning("⚠️ No data found in Deadline Alerts Log tab")
                return []
            
            # Skip header row
            data_rows = values[1:]
            
            # Convert to list of dictionaries
            alerts = []
            headers = ['Alert Timestamp', 'Organization', 'Proposal Title', 'Deadline', 'Urgency Level', 'Assigned To', 'Notes']
            
            for row in data_rows:
                # Skip empty rows
                if not any(cell.strip() for cell in row if cell):
                    continue
                
                # Create alert dictionary
                alert = {}
                for i, header in enumerate(headers):
                    alert[header] = row[i] if i < len(row) else ""
                
                alerts.append(alert)
            
            logger.info(f"✅ Retrieved {len(alerts)} alerts")
            return alerts
            
        except HttpError as e:
            logger.error(f"❌ HTTP error getting alerts: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error getting alerts: {e}")
            return []

# Global instance
sheets_integration = SheetsIntegration()
