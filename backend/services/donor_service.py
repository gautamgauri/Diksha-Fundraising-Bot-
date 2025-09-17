#!/usr/bin/env python3
"""
Donor Service - Unified interface for donor operations
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Import profile generator with fallback
try:
    from .donor_profile_generator import DonorProfileService
    PROFILE_GENERATOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Donor profile generator not available: {e}")
    PROFILE_GENERATOR_AVAILABLE = False
    DonorProfileService = None

class DonorService:
    """Service for donor-related operations"""
    
    def __init__(self, sheets_db=None):
        """Initialize with sheets database"""
        self.sheets_db = sheets_db
        
        # Initialize profile generator if available
        self.profile_generator = None
        if PROFILE_GENERATOR_AVAILABLE:
            try:
                self.profile_generator = DonorProfileService()
                logger.info("✅ Donor profile generator initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize profile generator: {e}")
                self.profile_generator = None
    
    def get_donor(self, donor_id: str) -> Optional[Dict[str, Any]]:
        """Get donor by ID (organization name)"""
        if not self.sheets_db or not self.sheets_db.initialized:
            return None
        
        try:
            # Convert donor_id back to organization name
            org_name = donor_id.replace("_", " ").title()
            
            # Find the organization
            org_data = self.sheets_db.get_org_by_name(org_name)
            if not org_data:
                return None
            
            # Convert to web UI format
            donor = {
                "id": donor_id,
                "organization_name": org_data.get("organization_name", ""),
                "current_stage": org_data.get("current_stage", "Initial Contact"),
                "assigned_to": org_data.get("assigned_to", ""),
                "next_action": org_data.get("next_action", ""),
                "next_action_date": org_data.get("next_action_date", ""),
                "last_contact_date": org_data.get("last_contact_date", ""),
                "sector_tags": org_data.get("sector_tags", ""),
                "probability": org_data.get("probability", 0),
                "updated_at": org_data.get("updated_at", ""),
                "alignment_score": org_data.get("alignment_score", 0),
                "contact_person": org_data.get("contact_person", ""),
                "contact_email": org_data.get("email", ""),
                "contact_role": org_data.get("contact_role", ""),
                "notes": org_data.get("notes", ""),
                "documents": []  # TODO: Implement document fetching
            }
            
            return donor
            
        except Exception as e:
            logger.error(f"Error getting donor {donor_id}: {e}")
            return None
    
    def get_all_donors(self) -> List[Dict[str, Any]]:
        """Get all donors from the pipeline (filtered for actual data)"""
        if not self.sheets_db or not self.sheets_db.initialized:
            return []
        
        try:
            # Get all organizations from the pipeline
            all_orgs = []
            pipeline = self.sheets_db.get_pipeline()
            for stage_orgs in pipeline.values():
                all_orgs.extend(stage_orgs)
            
            # Filter out empty records - only include records with actual organization names
            filtered_orgs = [
                org for org in all_orgs 
                if org.get("organization_name") and 
                   str(org.get("organization_name", "")).strip() != ""
            ]
            
            logger.info(f"Filtered {len(filtered_orgs)} actual records from {len(all_orgs)} total rows")
            
            # Convert to web UI format
            donors = []
            for org in filtered_orgs:
                donor_id = org.get("organization_name", "").replace(" ", "_").lower()
                donor = {
                    "id": donor_id,
                    "organization_name": org.get("organization_name", ""),
                    "current_stage": org.get("current_stage", "Initial Contact"),
                    "assigned_to": org.get("assigned_to", ""),
                    "next_action": org.get("next_action", ""),
                    "next_action_date": org.get("next_action_date", ""),
                    "last_contact_date": org.get("last_contact_date", ""),
                    "sector_tags": org.get("sector_tags", ""),
                    "probability": org.get("probability", 0),
                    "updated_at": org.get("updated_at", ""),
                    "alignment_score": org.get("alignment_score", 0),
                    "contact_person": org.get("contact_person", ""),
                    "contact_email": org.get("email", ""),
                    "contact_role": org.get("contact_role", ""),
                    "notes": org.get("notes", ""),
                    "documents": []  # TODO: Implement document fetching
                }
                donors.append(donor)
            
            return donors
            
        except Exception as e:
            logger.error(f"Error getting all donors: {e}")
            return []
    
    def get_data_quality_stats(self) -> Dict[str, Any]:
        """Get data quality statistics"""
        if not self.sheets_db or not self.sheets_db.initialized:
            return {"error": "Sheets not initialized"}
        
        try:
            # Get all organizations from the pipeline
            all_orgs = []
            pipeline = self.sheets_db.get_pipeline()
            for stage_orgs in pipeline.values():
                all_orgs.extend(stage_orgs)
            
            total_rows = len(all_orgs)
            
            # Count records with actual data
            records_with_org_name = len([
                org for org in all_orgs 
                if org.get("organization_name") and str(org.get("organization_name", "")).strip() != ""
            ])
            
            records_with_contact = len([
                org for org in all_orgs 
                if org.get("contact_person") and str(org.get("contact_person", "")).strip() != ""
            ])
            
            records_with_email = len([
                org for org in all_orgs 
                if org.get("email") and str(org.get("email", "")).strip() != ""
            ])
            
            records_with_stage = len([
                org for org in all_orgs 
                if org.get("current_stage") and str(org.get("current_stage", "")).strip() != ""
            ])
            
            return {
                "total_rows": total_rows,
                "records_with_organization_name": records_with_org_name,
                "records_with_contact_person": records_with_contact,
                "records_with_email": records_with_email,
                "records_with_stage": records_with_stage,
                "data_quality_percentage": round((records_with_org_name / total_rows * 100), 2) if total_rows > 0 else 0,
                "actual_records": records_with_org_name
            }
            
        except Exception as e:
            logger.error(f"Error getting data quality stats: {e}")
            return {"error": str(e)}
    
    def update_donor_stage(self, donor_id: str, stage: str) -> bool:
        """Update donor stage"""
        if not self.sheets_db or not self.sheets_db.initialized:
            return False
        
        try:
            # Convert donor_id back to organization name
            org_name = donor_id.replace("_", " ").title()
            
            # Update the stage
            return self.sheets_db.update_org_field(org_name, "current_stage", stage)
            
        except Exception as e:
            logger.error(f"Error updating donor stage: {e}")
            return False
    
    def update_donor_owner(self, donor_id: str, owner: str) -> bool:
        """Update donor owner/assignment"""
        if not self.sheets_db or not self.sheets_db.initialized:
            return False
        
        try:
            # Convert donor_id back to organization name
            org_name = donor_id.replace("_", " ").title()
            
            # Update the assignment
            return self.sheets_db.update_org_field(org_name, "assigned_to", owner)
            
        except Exception as e:
            logger.error(f"Error updating donor owner: {e}")
            return False
    
    def update_donor_notes(self, donor_id: str, notes: str) -> bool:
        """Update donor notes"""
        if not self.sheets_db or not self.sheets_db.initialized:
            return False
        
        try:
            # Convert donor_id back to organization name
            org_name = donor_id.replace("_", " ").title()
            
            # Update the notes
            return self.sheets_db.update_org_field(org_name, "notes", notes or "")
            
        except Exception as e:
            logger.error(f"Error updating donor notes: {e}")
            return False
    
    def search_donors(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for donors"""
        if not self.sheets_db or not self.sheets_db.initialized:
            return []
        
        try:
            # Use sheets_db search functionality
            matches = self.sheets_db.find_org(query, limit)
            
            # Convert to web UI format
            donors = []
            for match in matches:
                donor_id = match.get("organization_name", "").replace(" ", "_").lower()
                donor = {
                    "id": donor_id,
                    "organization_name": match.get("organization_name", ""),
                    "current_stage": match.get("current_stage", "Initial Contact"),
                    "assigned_to": match.get("assigned_to", ""),
                    "next_action": match.get("next_action", ""),
                    "next_action_date": match.get("next_action_date", ""),
                    "last_contact_date": match.get("last_contact_date", ""),
                    "sector_tags": match.get("sector_tags", ""),
                    "probability": match.get("probability", 0),
                    "updated_at": match.get("updated_at", ""),
                    "alignment_score": match.get("alignment_score", 0),
                    "contact_person": match.get("contact_person", ""),
                    "contact_email": match.get("email", ""),
                    "contact_role": match.get("contact_role", ""),
                    "notes": match.get("notes", ""),
                    "documents": [],
                    "similarity_score": match.get("similarity_score", 0),
                    "exact_match": match.get("exact_match", False)
                }
                donors.append(donor)
            
            return donors
            
        except Exception as e:
            logger.error(f"Error searching donors: {e}")
            return []
    
    def check_existing_donor(self, donor_name: str) -> Dict[str, Any]:
        """Check if donor already exists in the database"""
        try:
            if not self.sheets_db or not self.sheets_db.initialized:
                return {
                    "exists": False,
                    "error": "Database not available for checking"
                }
            
            # Get all organizations from database
            pipeline = self.sheets_db.get_pipeline()
            existing_donors = []
            for stage_orgs in pipeline.values():
                existing_donors.extend(stage_orgs)
            donor_name_clean = donor_name.strip().lower()
            
            # Search for matching donor
            for donor in existing_donors:
                existing_name = donor.get("organization_name", "").strip().lower()
                if existing_name == donor_name_clean:
                    logger.info(f"Found existing donor: {donor_name}")
                    return {
                        "exists": True,
                        "donor_data": donor,
                        "message": f"Donor '{donor_name}' already exists in database"
                    }
            
            logger.info(f"No existing donor found for: {donor_name}")
            return {
                "exists": False,
                "message": f"No existing donor found for '{donor_name}'"
            }
            
        except Exception as e:
            logger.error(f"Error checking existing donor {donor_name}: {e}")
            return {
                "exists": False,
                "error": str(e)
            }
    
    def generate_donor_profile(self, donor_name: str, export_to_docs: bool = True, force_generate: bool = False) -> Dict[str, Any]:
        """Generate an AI-powered donor profile with optional database checking"""
        if not self.profile_generator:
            return {
                "success": False,
                "error": "Profile generator not available. Check AI model configuration."
            }
        
        try:
            # Check if donor already exists (unless force generation is requested)
            existing_check = None
            if not force_generate:
                existing_check = self.check_existing_donor(donor_name)
                
                if existing_check.get("exists"):
                    # Return existing donor info instead of generating
                    return {
                        "success": True,
                        "already_exists": True,
                        "existing_donor": existing_check.get("donor_data"),
                        "message": existing_check.get("message"),
                        "suggestion": "Use 'force_generate=true' to create a new profile anyway"
                    }
            
            # Use default profiles folder ID from environment or config
            profiles_folder_id = "1Zrk26Mn0QtH9_9WYq4fPAaIdONOAIkcS"  # From original Colab code
            
            logger.info(f"Generating new profile for: {donor_name}")
            result = self.profile_generator.generate_donor_profile(
                donor_name=donor_name,
                export_to_docs=export_to_docs,
                folder_id=profiles_folder_id
            )
            
            # Add existing check info to result
            if existing_check:
                result["existing_check"] = existing_check
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating donor profile for {donor_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_donor_database(self, donor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update the Google Sheets database with donor information"""
        try:
            if not self.sheets_db or not self.sheets_db.initialized:
                return {
                    "success": False,
                    "error": "Google Sheets database not initialized"
                }
            
            # Extract donor information
            donor_name = donor_data.get("donor_name", "").strip()
            if not donor_name:
                return {
                    "success": False,
                    "error": "Donor name is required"
                }
            
            # Check if donor already exists first
            # Check if we have an original name to search for (for updates)
            original_name = donor_data.get("original_name", donor_name)

            pipeline = self.sheets_db.get_pipeline()
            existing_donors = []
            for stage_orgs in pipeline.values():
                existing_donors.extend(stage_orgs)
            existing_donor = None

            # Try to find existing donor by original name first, then by new name
            for donor in existing_donors:
                org_name = donor.get("organization_name", "").strip().lower()
                if (org_name == original_name.lower() or
                    org_name == donor_name.lower()):
                    existing_donor = donor
                    break

            # Prepare donor record - use provided data or sensible defaults
            donor_record = {
                "organization_name": donor_name,
                "contact_person": donor_data.get("contact_person", ""),
                "contact_email": donor_data.get("contact_email", ""),
                "contact_role": donor_data.get("contact_role", ""),
                "website": donor_data.get("website", ""),
                "sector_tags": donor_data.get("sector_tags", ""),
                "current_stage": donor_data.get("current_stage", "Initial Outreach"),
                "assigned_to": donor_data.get("assigned_to", ""),
                "expected_amount": donor_data.get("expected_amount", 0),
                "probability": donor_data.get("probability", 25),
                "notes": donor_data.get("notes", ""),
                "next_action": donor_data.get("next_action", "Initial follow-up"),
                "next_action_date": donor_data.get("next_action_date", ""),
                "alignment_score": donor_data.get("alignment_score", 0),
                "profile_generated": donor_data.get("profile_generated", "Yes"),
                "document_url": donor_data.get("document_url", ""),
                "pdf_url": donor_data.get("pdf_url", "")
            }

            # Only set date_added and profile_date for new records, preserve existing for updates
            if existing_donor:
                # Preserve existing dates for updates
                donor_record["date_added"] = existing_donor.get("date_added", datetime.now().strftime("%Y-%m-%d"))
                donor_record["profile_date"] = existing_donor.get("profile_date", datetime.now().strftime("%Y-%m-%d"))
                donor_record["last_contact_date"] = existing_donor.get("last_contact_date", "")
            else:
                # Set dates for new records
                donor_record["date_added"] = datetime.now().strftime("%Y-%m-%d")
                donor_record["profile_date"] = datetime.now().strftime("%Y-%m-%d")
                donor_record["last_contact_date"] = ""
            
            if existing_donor:
                # Update existing donor
                logger.info(f"Updating existing donor: {donor_name}")
                donor_record["id"] = existing_donor.get("id", "")
                result = self.sheets_db.update_organization(donor_record["id"], donor_record)
                
                if result:
                    return {
                        "success": True,
                        "action": "updated",
                        "donor_name": donor_name,
                        "message": f"Successfully updated donor: {donor_name}"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to update donor: {donor_name}"
                    }
            else:
                # Add new donor
                logger.info(f"Adding new donor: {donor_name}")
                result = self.sheets_db.add_organization(donor_record)
                
                if result:
                    return {
                        "success": True,
                        "action": "added",
                        "donor_name": donor_name,
                        "message": f"Successfully added new donor: {donor_name}"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to add donor: {donor_name}"
                    }
                    
        except Exception as e:
            logger.error(f"Error updating donor database: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_profile_generator_status(self) -> Dict[str, Any]:
        """Get status of the profile generator"""
        if not self.profile_generator:
            return {
                "available": False,
                "error": "Profile generator not initialized",
                "models": {},
                "google_docs": False
            }
        
        try:
            # Get models in a JSON-safe way
            models = self.profile_generator.get_available_models()

            return {
                "available": True,
                "models": models,
                "google_docs": self.profile_generator.is_google_docs_available()
            }
        except Exception as e:
            # Log the full error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Profile generator status error: {type(e).__name__}: {str(e)}")

            return {
                "available": False,
                "error": str(e),
                "models": {},
                "google_docs": False
            }

    def get_available_models(self) -> Dict[str, Any]:
        """Get available AI models from the profile generator"""
        if not self.profile_generator:
            return {}

        try:
            return self.profile_generator.get_available_models()
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return {}

    def detect_duplicates(self) -> Dict[str, Any]:
        """Detect duplicate organizations in the database"""
        try:
            if not self.sheets_db or not self.sheets_db.initialized:
                return {
                    "success": False,
                    "error": "Google Sheets database not initialized"
                }

            # Get all organizations from all stages
            pipeline = self.sheets_db.get_pipeline()
            all_orgs = []
            for stage_orgs in pipeline.values():
                all_orgs.extend(stage_orgs)

            # Track duplicates by organization name (case-insensitive)
            org_names = {}
            duplicates = []

            for org in all_orgs:
                org_name = org.get('organization_name', '').strip().lower()
                if not org_name:
                    continue

                if org_name in org_names:
                    # Found a duplicate
                    if org_name not in [d['name'] for d in duplicates]:
                        # Add both original and duplicate to the list
                        duplicates.append({
                            'name': org_name,
                            'original_name': org.get('organization_name', ''),
                            'count': 2,
                            'records': [org_names[org_name], org]
                        })
                    else:
                        # Add this record to existing duplicate group
                        for d in duplicates:
                            if d['name'] == org_name:
                                d['count'] += 1
                                d['records'].append(org)
                                break
                else:
                    org_names[org_name] = org

            return {
                "success": True,
                "duplicates_found": len(duplicates),
                "duplicates": duplicates,
                "total_organizations": len(all_orgs)
            }

        except Exception as e:
            logger.error(f"Error detecting duplicates: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def remove_duplicates(self, keep_strategy: str = "newest") -> Dict[str, Any]:
        """
        Remove duplicate organizations from the database

        Args:
            keep_strategy: Strategy for which record to keep ("newest", "oldest", "most_complete")
        """
        try:
            if not self.sheets_db or not self.sheets_db.initialized:
                return {
                    "success": False,
                    "error": "Google Sheets database not initialized"
                }

            # First detect duplicates
            duplicate_result = self.detect_duplicates()
            if not duplicate_result.get("success"):
                return duplicate_result

            duplicates = duplicate_result.get("duplicates", [])
            if not duplicates:
                return {
                    "success": True,
                    "message": "No duplicates found",
                    "removed_count": 0
                }

            removed_count = 0
            removed_records = []

            for duplicate_group in duplicates:
                records = duplicate_group['records']

                # Determine which record to keep based on strategy
                if keep_strategy == "newest":
                    # Keep the one with the most recent date_added or last record
                    keep_record = max(records, key=lambda x: x.get('date_added', '1900-01-01'))
                elif keep_strategy == "oldest":
                    # Keep the one with the oldest date_added or first record
                    keep_record = min(records, key=lambda x: x.get('date_added', '2099-12-31'))
                else:  # most_complete
                    # Keep the one with the most non-empty fields
                    keep_record = max(records, key=lambda x: sum(1 for v in x.values() if v and str(v).strip()))

                # Remove all other records
                for record in records:
                    if record != keep_record:
                        record_id = record.get('id', '')
                        org_name = record.get('organization_name', '')

                        if record_id:
                            # Try to remove by updating the record to empty values
                            success = self._remove_organization_record(record_id)
                            if success:
                                removed_count += 1
                                removed_records.append({
                                    'id': record_id,
                                    'name': org_name,
                                    'stage': record.get('current_stage', '')
                                })
                                logger.info(f"Removed duplicate record: {org_name} (ID: {record_id})")

            return {
                "success": True,
                "message": f"Successfully removed {removed_count} duplicate records",
                "removed_count": removed_count,
                "removed_records": removed_records,
                "strategy_used": keep_strategy
            }

        except Exception as e:
            logger.error(f"Error removing duplicates: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _remove_organization_record(self, record_id: str) -> bool:
        """
        Remove an organization record by clearing its data
        Note: We clear the data rather than deleting the row to maintain sheet structure
        """
        try:
            # Create an empty record to overwrite the duplicate
            empty_record = {field: "" for field in FIELD_MAPPING.keys()}
            empty_record['id'] = record_id  # Keep the ID for identification

            # Update the record with empty values
            return self.sheets_db.update_organization(record_id, empty_record)

        except Exception as e:
            logger.error(f"Error removing organization record {record_id}: {e}")
            return False
