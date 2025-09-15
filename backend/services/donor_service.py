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
    
    def generate_donor_profile(self, donor_name: str, export_to_docs: bool = True) -> Dict[str, Any]:
        """Generate an AI-powered donor profile"""
        if not self.profile_generator:
            return {
                "success": False,
                "error": "Profile generator not available. Check AI model configuration."
            }
        
        try:
            # Use default profiles folder ID from environment or config
            profiles_folder_id = "1Zrk26Mn0QtH9_9WYq4fPAaIdONOAIkcS"  # From original Colab code
            
            logger.info(f"Generating profile for: {donor_name}")
            result = self.profile_generator.generate_donor_profile(
                donor_name=donor_name,
                export_to_docs=export_to_docs,
                folder_id=profiles_folder_id
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating donor profile for {donor_name}: {e}")
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
            return {
                "available": True,
                "models": self.profile_generator.get_available_models(),
                "google_docs": self.profile_generator.is_google_docs_available()
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "models": {},
                "google_docs": False
            }
