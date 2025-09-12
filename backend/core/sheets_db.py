"""
Google Sheets Database Module
Handles reading and writing to the Diksha fundraising pipeline Google Sheet
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Try to import Google API dependencies with fallback
try:
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Google API dependencies not available: {e}")
    GOOGLE_API_AVAILABLE = False
    # Create mock class for fallback
    class HttpError(Exception):
        pass

# Optional import for fuzzy matching
try:
    from fuzzywuzzy import fuzz
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    FUZZYWUZZY_AVAILABLE = False

# Try to import google_auth with fallback
try:
    from google_auth import create_google_clients
    GOOGLE_AUTH_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Google auth not available: {e}")
    GOOGLE_AUTH_AVAILABLE = False
    # Create mock function for fallback
    def create_google_clients(*args, **kwargs):
        raise ImportError("Google auth not available")

logger = logging.getLogger(__name__)

# Log fuzzywuzzy availability after logger is defined
if not FUZZYWUZZY_AVAILABLE:
    logger.warning("⚠️ fuzzywuzzy not available - using basic string matching")

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
        self.available_tabs = []
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
        """Test access to the Google Sheet and discover all tabs"""
        try:
            # First, get all sheet metadata to discover tabs
            sheet_metadata = self.sheets_service.spreadsheets().get(
                spreadsheetId=self.sheet_id
            ).execute()
            
            # Extract all tab names
            self.available_tabs = []
            for sheet in sheet_metadata.get('sheets', []):
                tab_name = sheet['properties']['title']
                self.available_tabs.append(tab_name)
            
            logger.info(f"✅ Successfully connected to spreadsheet")
            logger.info(f"📋 Available tabs: {self.available_tabs}")
            
            # Test access to the main tab
            if self.sheet_tab in self.available_tabs:
                range_name = f"{self.sheet_tab}!A1:M1"
                result = self.sheets_service.spreadsheets().values().get(
                    spreadsheetId=self.sheet_id,
                    range=range_name
                ).execute()
                
                headers = result.get('values', [[]])[0]
                logger.info(f"✅ Successfully accessed main tab: {self.sheet_tab}")
                logger.info(f"📋 Headers found: {headers}")
                self.initialized = True
            else:
                logger.warning(f"⚠️ Main tab '{self.sheet_tab}' not found. Available tabs: {self.available_tabs}")
                # Use the first available tab as fallback
                if self.available_tabs:
                    self.sheet_tab = self.available_tabs[0]
                    logger.info(f"🔄 Using first available tab as fallback: {self.sheet_tab}")
                    self.initialized = True
            
        except HttpError as e:
            if e.resp.status == 404:
                logger.error(f"❌ Spreadsheet not found or no access")
            else:
                logger.error(f"❌ Failed to access spreadsheet: {e}")
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
    
    def get_interaction_log(self) -> List[Dict[str, Any]]:
        """
        Get interaction log data from the Interaction Log tab
        
        Returns:
            List[Dict]: Interaction log entries
        """
        if not self.initialized:
            logger.error("❌ SheetsDB not initialized")
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
    
    def get_all_tabs(self) -> List[str]:
        """
        Get list of all available tabs in the spreadsheet
        
        Returns:
            List[str]: List of tab names
        """
        return self.available_tabs.copy()
    
    def get_tab_data(self, tab_name: str) -> List[List[str]]:
        """
        Get all data from a specific tab
        
        Args:
            tab_name (str): Name of the tab to read
            
        Returns:
            List[List[str]]: Raw data from the tab
        """
        if not self.initialized:
            logger.error("❌ SheetsDB not initialized")
            return []
        
        if tab_name not in self.available_tabs:
            logger.error(f"❌ Tab '{tab_name}' not found. Available tabs: {self.available_tabs}")
            return []
        
        try:
            # Read all data from the specified tab
            range_name = f"{tab_name}!A:Z"  # Read more columns to be safe
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            logger.info(f"✅ Retrieved {len(values)} rows from tab '{tab_name}'")
            return values
            
        except HttpError as e:
            logger.error(f"❌ HTTP error reading tab '{tab_name}': {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error reading tab '{tab_name}': {e}")
            return []
    
    def search_across_all_tabs(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for organizations across all tabs
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results to return
            
        Returns:
            List[Dict]: Matching organizations with tab information
        """
        if not self.initialized:
            logger.error("❌ SheetsDB not initialized")
            return []
        
        all_matches = []
        query_lower = query.lower()
        
        for tab_name in self.available_tabs:
            try:
                # Get data from this tab
                tab_data = self.get_tab_data(tab_name)
                if not tab_data:
                    continue
                
                # Skip header row
                data_rows = tab_data[1:] if len(tab_data) > 1 else []
                
                # Search in organization names (assuming column A)
                for row in data_rows:
                    if not row or len(row) == 0:
                        continue
                    
                    org_name = row[0] if len(row) > 0 else ""
                    if not org_name:
                        continue
                    
                    # Check for matches
                    exact_match = query_lower in org_name.lower()
                    
                    if FUZZYWUZZY_AVAILABLE:
                        fuzzy_score = fuzz.partial_ratio(query_lower, org_name.lower())
                        if exact_match or fuzzy_score > 60:
                            all_matches.append({
                                'organization_name': org_name,
                                'tab_name': tab_name,
                                'similarity_score': fuzzy_score,
                                'exact_match': exact_match,
                                'row_data': row
                            })
                    else:
                        if exact_match:
                            all_matches.append({
                                'organization_name': org_name,
                                'tab_name': tab_name,
                                'similarity_score': 100,
                                'exact_match': True,
                                'row_data': row
                            })
                            
            except Exception as e:
                logger.error(f"❌ Error searching in tab '{tab_name}': {e}")
                continue
        
        # Sort by relevance (exact matches first, then by fuzzy score)
        all_matches.sort(key=lambda x: (not x['exact_match'], -x['similarity_score']))
        
        # Return top matches
        result = all_matches[:limit]
        logger.info(f"🔍 Found {len(result)} matches across all tabs for query '{query}'")
        return result
    
    def get_tab_summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Get summary information for all tabs
        
        Returns:
            Dict: Summary information for each tab
        """
        if not self.initialized:
            logger.error("❌ SheetsDB not initialized")
            return {}
        
        summary = {}
        
        for tab_name in self.available_tabs:
            try:
                tab_data = self.get_tab_data(tab_name)
                if not tab_data:
                    summary[tab_name] = {
                        'row_count': 0,
                        'column_count': 0,
                        'has_headers': False,
                        'status': 'empty'
                    }
                    continue
                
                row_count = len(tab_data)
                column_count = len(tab_data[0]) if tab_data else 0
                has_headers = row_count > 1
                
                summary[tab_name] = {
                    'row_count': row_count,
                    'column_count': column_count,
                    'has_headers': has_headers,
                    'status': 'active',
                    'headers': tab_data[0] if has_headers else []
                }
                
            except Exception as e:
                logger.error(f"❌ Error getting summary for tab '{tab_name}': {e}")
                summary[tab_name] = {
                    'row_count': 0,
                    'column_count': 0,
                    'has_headers': False,
                    'status': 'error',
                    'error': str(e)
                }
        
        return summary
    
    def get_drive_files(self, folder_id: str = None) -> List[Dict[str, Any]]:
        """
        Get files from Google Drive folder
        
        Args:
            folder_id (str): Google Drive folder ID (optional)
            
        Returns:
            List[Dict]: List of files with metadata
        """
        if not self.initialized or not self.drive_service:
            logger.error("❌ Drive service not available")
            return []
        
        try:
            # If no folder_id provided, use the donor profiles folder
            if not folder_id:
                folder_id = "1zfT_oXgcIMSubeF3TtSNflkNvTx__dBK"  # Donor profiles folder
            
            # Query files in the folder
            query = f"'{folder_id}' in parents and trashed=false"
            results = self.drive_service.files().list(
                q=query,
                fields="files(id, name, mimeType, size, modifiedTime, webViewLink, parents)"
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"✅ Found {len(files)} files in Drive folder {folder_id}")
            
            return files
            
        except Exception as e:
            logger.error(f"❌ Error accessing Drive folder: {e}")
            return []
    
    def get_institutional_grants_files(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get files from all institutional grants subfolders
        
        Returns:
            Dict: Files organized by subfolder
        """
        if not self.initialized or not self.drive_service:
            logger.error("❌ Drive service not available")
            return {}
        
        try:
            institutional_folder_id = "1MDCBas01pwIeeLfhz4Nay06GqhUbRTQO"
            subfolders = {
                "Templates": None,
                "Secured Grants": None,
                "Resources": None,
                "Active Prospects": None,
                "Archive": None
            }
            
            # First, get all subfolders
            query = f"'{institutional_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.drive_service.files().list(
                q=query,
                fields="files(id, name)"
            ).execute()
            
            folders = results.get('files', [])
            logger.info(f"✅ Found {len(folders)} subfolders in institutional grants folder")
            
            # Map folder names to IDs
            for folder in folders:
                folder_name = folder['name']
                if folder_name in subfolders:
                    subfolders[folder_name] = folder['id']
            
            # Get files from each subfolder
            all_files = {}
            for folder_name, folder_id in subfolders.items():
                if folder_id:
                    files = self.get_drive_files(folder_id)
                    all_files[folder_name] = files
                    logger.info(f"📁 {folder_name}: {len(files)} files")
                else:
                    all_files[folder_name] = []
                    logger.warning(f"⚠️ Subfolder '{folder_name}' not found")
            
            return all_files
            
        except Exception as e:
            logger.error(f"❌ Error accessing institutional grants folder: {e}")
            return {}
    
    def search_drive_files(self, query: str, folder_id: str = None) -> List[Dict[str, Any]]:
        """
        Search for files in Google Drive folder by name
        
        Args:
            query (str): Search query
            folder_id (str): Google Drive folder ID (optional)
            
        Returns:
            List[Dict]: Matching files
        """
        if not self.initialized or not self.drive_service:
            logger.error("❌ Drive service not available")
            return []
        
        try:
            # If no folder_id provided, use the shared folder
            if not folder_id:
                folder_id = "1zfT_oXgcIMSubeF3TtSNflkNvTx__dBK"  # Your shared folder
            
            # Search for files containing the query in name
            search_query = f"'{folder_id}' in parents and name contains '{query}' and trashed=false"
            results = self.drive_service.files().list(
                q=search_query,
                fields="files(id, name, mimeType, size, modifiedTime, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"🔍 Found {len(files)} files matching '{query}' in Drive folder")
            
            return files
            
        except Exception as e:
            logger.error(f"❌ Error searching Drive files: {e}")
            return []
    
    def get_file_content(self, file_id: str) -> str:
        """
        Get text content from a Google Drive file (for text-based files)
        
        Args:
            file_id (str): Google Drive file ID
            
        Returns:
            str: File content as text
        """
        if not self.initialized or not self.drive_service:
            logger.error("❌ Drive service not available")
            return ""
        
        try:
            # Get file metadata first
            file_metadata = self.drive_service.files().get(fileId=file_id).execute()
            mime_type = file_metadata.get('mimeType', '')
            
            # Only process text-based files
            if 'text/' in mime_type or 'application/pdf' in mime_type:
                # For now, return file info - full content extraction would need additional libraries
                return f"File: {file_metadata.get('name', 'Unknown')} (Type: {mime_type})"
            else:
                return f"File: {file_metadata.get('name', 'Unknown')} (Binary file - content not extractable)"
                
        except Exception as e:
            logger.error(f"❌ Error getting file content: {e}")
            return ""
    
    def search_all_drive_folders(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for files across all accessible Drive folders
        
        Args:
            query (str): Search query
            
        Returns:
            Dict: Search results organized by folder
        """
        if not self.initialized or not self.drive_service:
            logger.error("❌ Drive service not available")
            return {}
        
        try:
            results = {
                "donor_profiles": [],
                "institutional_grants": {
                    "Templates": [],
                    "Secured Grants": [],
                    "Resources": [],
                    "Active Prospects": [],
                    "Archive": []
                }
            }
            
            # Search in donor profiles folder
            donor_files = self.search_drive_files(query, "1zfT_oXgcIMSubeF3TtSNflkNvTx__dBK")
            results["donor_profiles"] = donor_files
            
            # Search in institutional grants subfolders
            institutional_files = self.get_institutional_grants_files()
            for folder_name, files in institutional_files.items():
                # Filter files by query
                matching_files = []
                for file in files:
                    if query.lower() in file.get('name', '').lower():
                        matching_files.append(file)
                results["institutional_grants"][folder_name] = matching_files
            
            total_matches = len(donor_files) + sum(len(files) for files in results["institutional_grants"].values())
            logger.info(f"🔍 Found {total_matches} total matches for '{query}' across all Drive folders")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching all Drive folders: {e}")
            return {}
    
    def get_drive_summary(self) -> Dict[str, Any]:
        """
        Get summary of all accessible Drive folders and files
        
        Returns:
            Dict: Summary information
        """
        if not self.initialized or not self.drive_service:
            logger.error("❌ Drive service not available")
            return {}
        
        try:
            summary = {
                "donor_profiles": {
                    "folder_id": "1zfT_oXgcIMSubeF3TtSNflkNvTx__dBK",
                    "file_count": 0,
                    "files": []
                },
                "institutional_grants": {
                    "folder_id": "1MDCBas01pwIeeLfhz4Nay06GqhUbRTQO",
                    "subfolders": {}
                }
            }
            
            # Get donor profiles summary
            donor_files = self.get_drive_files("1zfT_oXgcIMSubeF3TtSNflkNvTx__dBK")
            summary["donor_profiles"]["file_count"] = len(donor_files)
            summary["donor_profiles"]["files"] = donor_files[:5]  # First 5 files as sample
            
            # Get institutional grants summary
            institutional_files = self.get_institutional_grants_files()
            for folder_name, files in institutional_files.items():
                summary["institutional_grants"]["subfolders"][folder_name] = {
                    "file_count": len(files),
                    "sample_files": files[:3]  # First 3 files as sample
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error getting Drive summary: {e}")
            return {}
