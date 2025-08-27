"""
Google Sheets Database Module
Handles reading and writing to the Diksha fundraising pipeline Google Sheet
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from googleapiclient.errors import HttpError

# Optional import for fuzzy matching
try:
    from fuzzywuzzy import fuzz
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    FUZZYWUZZY_AVAILABLE = False
    logger.warning("⚠️ fuzzywuzzy not available - using basic string matching")

from google_auth import create_google_clients

logger = logging.getLogger(__name__)

# Column mappings for the Google Sheet
COLUMN_MAPPINGS = {
    'organization_name': 'A',
    'contact_person': 'B', 
    'email': 'C',
    'phone': 'D',
    'current_stage': 'E',
    'previous_stage': 'F',
    'sector_tags': 'G',
    'geography': 'H',
    'assigned_to': 'I',
    'next_action': 'J',
    'next_action_date': 'K',
    'notes': 'L',
    'last_updated': 'M'
}

class SheetsDB:
    """
    Database class for managing Diksha fundraising pipeline data in Google Sheets
    """
    
    def __init__(self):
        """Initialize the SheetsDB with Google API clients"""
        self.sheets_service = None
        self.drive_service = None
        self.sheet_id = None
        self.sheet_tab = None
        self.initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialize Google API clients and sheet configuration"""
        try:
            # Get sheet configuration from environment variables
            self.sheet_id = os.environ.get('MAIN_SHEET_ID')
            self.sheet_tab = os.environ.get('MAIN_SHEET_TAB', 'Pipeline Tracker')
            
            if not self.sheet_id:
                logger.warning("⚠️ MAIN_SHEET_ID environment variable not set - running in offline mode")
                return
            
            # Create Google API clients
            self.sheets_service, self.drive_service = create_google_clients()
            if not self.sheets_service or not self.drive_service:
                logger.warning("⚠️ Failed to create Google API clients - running in offline mode")
                return
            
            # Test connection by reading the sheet
            self._test_sheet_access()
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize SheetsDB: {e} - running in offline mode")
    
    def _test_sheet_access(self):
        """Test access to the Google Sheet"""
        try:
            # Try to read the first row to verify access
            range_name = f"{self.sheet_tab}!A1:M1"
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            headers = result.get('values', [[]])[0]
            logger.info(f"✅ Successfully connected to sheet: {self.sheet_tab}")
            logger.info(f"📋 Headers found: {headers}")
            self.initialized = True
            
        except HttpError as e:
            if e.resp.status == 404:
                logger.error(f"❌ Sheet '{self.sheet_tab}' not found in spreadsheet")
            else:
                logger.error(f"❌ Failed to access sheet: {e}")
        except Exception as e:
            logger.error(f"❌ Error testing sheet access: {e}")
    
    def get_pipeline(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all pipeline data grouped by current stage
        
        Returns:
            Dict[str, List[Dict]]: Pipeline data grouped by stage
        """
        if not self.initialized:
            logger.error("❌ SheetsDB not initialized")
            return {}
        
        try:
            # Read all data from the sheet
            range_name = f"{self.sheet_tab}!A:M"
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                logger.warning("⚠️ No data found in sheet")
                return {}
            
            # Skip header row
            data_rows = values[1:]
            
            # Group by current stage
            pipeline = {}
            for row in data_rows:
                # Ensure row has enough columns
                while len(row) < len(COLUMN_MAPPINGS):
                    row.append('')
                
                org_data = {
                    'organization_name': row[0] or '',
                    'contact_person': row[1] or '',
                    'email': row[2] or '',
                    'phone': row[3] or '',
                    'current_stage': row[4] or '',
                    'previous_stage': row[5] or '',
                    'sector_tags': row[6] or '',
                    'geography': row[7] or '',
                    'assigned_to': row[8] or '',
                    'next_action': row[9] or '',
                    'next_action_date': row[10] or '',
                    'notes': row[11] or '',
                    'last_updated': row[12] or ''
                }
                
                stage = org_data['current_stage'] or 'Uncategorized'
                if stage not in pipeline:
                    pipeline[stage] = []
                pipeline[stage].append(org_data)
            
            logger.info(f"✅ Retrieved {len(data_rows)} organizations grouped by {len(pipeline)} stages")
            return pipeline
            
        except HttpError as e:
            logger.error(f"❌ HTTP error getting pipeline data: {e}")
            return {}
        except Exception as e:
            logger.error(f"❌ Error getting pipeline data: {e}")
            return {}
    
    def find_org(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fuzzy search for organizations by name
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results to return
            
        Returns:
            List[Dict]: Matching organizations with similarity scores
        """
        if not self.initialized:
            logger.error("❌ SheetsDB not initialized")
            return []
        
        try:
            # Get all organizations
            pipeline = self.get_pipeline()
            all_orgs = []
            for stage_orgs in pipeline.values():
                all_orgs.extend(stage_orgs)
            
            # Perform fuzzy search
            matches = []
            query_lower = query.lower()
            
            for org in all_orgs:
                org_name = org['organization_name']
                if not org_name:
                    continue
                
                # Calculate similarity scores
                exact_match = query_lower in org_name.lower()
                
                if FUZZYWUZZY_AVAILABLE:
                    fuzzy_score = fuzz.partial_ratio(query_lower, org_name.lower())
                    if exact_match or fuzzy_score > 60:  # Threshold for fuzzy matching
                        matches.append({
                            **org,
                            'similarity_score': fuzzy_score,
                            'exact_match': exact_match
                        })
                else:
                    # Basic string matching fallback
                    fuzzy_score = 100 if exact_match else 0
                    if exact_match:
                        matches.append({
                            **org,
                            'similarity_score': fuzzy_score,
                            'exact_match': exact_match
                        })
            
            # Sort by relevance (exact matches first, then by fuzzy score)
            matches.sort(key=lambda x: (not x['exact_match'], -x['similarity_score']))
            
            # Return top matches
            result = matches[:limit]
            logger.info(f"🔍 Found {len(result)} matches for query '{query}'")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error searching organizations: {e}")
            return []
    
    def get_org_by_name(self, org_name: str) -> Optional[Dict[str, Any]]:
        """
        Get organization data by exact name match
        
        Args:
            org_name (str): Exact organization name
            
        Returns:
            Dict: Organization data or None if not found
        """
        if not self.initialized:
            return None
        
        try:
            # Get all organizations
            pipeline = self.get_pipeline()
            all_orgs = []
            for stage_orgs in pipeline.values():
                all_orgs.extend(stage_orgs)
            
            # Find exact match
            for org in all_orgs:
                if org['organization_name'].lower() == org_name.lower():
                    return org
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting organization by name: {e}")
            return None
    
    def update_org_field(self, org_name: str, field: str, value: str) -> bool:
        """
        Update a specific field for an organization
        
        Args:
            org_name (str): Organization name
            field (str): Field to update
            value (str): New value
            
        Returns:
            bool: True if update successful, False otherwise
        """
        if not self.initialized:
            return False
        
        try:
            # Find the organization row
            range_name = f"{self.sheet_tab}!A:A"
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return False
            
            # Find the row number (1-indexed, skip header)
            row_number = None
            for i, row in enumerate(values[1:], start=2):  # Start from row 2 (skip header)
                if row and row[0].lower() == org_name.lower():
                    row_number = i
                    break
            
            if not row_number:
                logger.error(f"❌ Organization '{org_name}' not found")
                return False
            
            # Get column letter for the field
            col_letter = COLUMN_MAPPINGS.get(field)
            if not col_letter:
                logger.error(f"❌ Unknown field: {field}")
                return False
            
            # Update the cell
            range_name = f"{self.sheet_tab}!{col_letter}{row_number}"
            self.sheets_service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body={'values': [[value]]}
            ).execute()
            
            # Update last_updated timestamp
            timestamp_range = f"{self.sheet_tab}!M{row_number}"
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.sheets_service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=timestamp_range,
                valueInputOption='RAW',
                body={'values': [[timestamp]]}
            ).execute()
            
            logger.info(f"✅ Updated {field} for '{org_name}' to '{value}'")
            return True
            
        except HttpError as e:
            logger.error(f"❌ HTTP error updating organization: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error updating organization: {e}")
            return False
    
    def get_stages(self) -> List[str]:
        """
        Get list of all current stages in the pipeline
        
        Returns:
            List[str]: List of stage names
        """
        pipeline = self.get_pipeline()
        return list(pipeline.keys())
    
    def get_orgs_by_stage(self, stage: str) -> List[Dict[str, Any]]:
        """
        Get all organizations in a specific stage
        
        Args:
            stage (str): Stage name
            
        Returns:
            List[Dict]: Organizations in the specified stage
        """
        pipeline = self.get_pipeline()
        return pipeline.get(stage, [])
