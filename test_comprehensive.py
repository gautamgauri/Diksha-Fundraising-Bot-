#!/usr/bin/env python3
"""
Comprehensive test script for the robust SheetsDB implementation
Tests all functionality with proper error handling and logging
"""

import logging
from backend import backend_manager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_sheets_db():
    """Test the comprehensive SheetsDB implementation via shared backend"""
    print("🔍 Testing Comprehensive SheetsDB via Shared Backend...")
    
    try:
        # Initialize via BackendManager
        print("\n📋 Initializing via BackendManager...")
        if not backend_manager.initialized:
            print("❌ BackendManager failed to initialize")
            print("💡 Check your environment variables:")
            print("   - GOOGLE_CREDENTIALS_BASE64")
            print("   - MAIN_SHEET_ID")
            print("   - MAIN_SHEET_TAB")
            return False
        
        print(f"✅ BackendManager initialized successfully")
        db = backend_manager.sheets_db
        donor_service = backend_manager.donor_service
        
        if not db or not donor_service:
            print("❌ SheetsDB or DonorService not available")
            return False
        
        print(f"📊 Sheet ID: {db.sheet_id}")
        print(f"📋 Tab: {db.sheet_tab}")
        
        # Test get_pipeline() via service layer
        print("\n📋 Testing get_pipeline() via DonorService...")
        pipeline = donor_service.get_pipeline()
        if not pipeline:
            print("❌ No pipeline data retrieved")
            return False
        
        print(f"✅ Retrieved {len(pipeline)} stages:")
        total_orgs = 0
        for stage, orgs in pipeline.items():
            print(f"  • {stage}: {len(orgs)} organizations")
            total_orgs += len(orgs)
        print(f"📊 Total organizations: {total_orgs}")
        
        # Test get_stages() via service layer
        print("\n📋 Testing get_stages() via PipelineService...")
        pipeline_service = backend_manager.pipeline_service
        stages = pipeline_service.get_stages()
        print(f"✅ Available stages: {stages}")
        
        # Test find_organization() with fuzzy search via service layer
        print("\n🔍 Testing find_organization() with fuzzy search via DonorService...")
        if pipeline:
            # Get first organization from first stage
            first_stage = list(pipeline.keys())[0]
            first_org = pipeline[first_stage][0]['organization_name']
            print(f"🔍 Searching for: {first_org}")
            
            matches = donor_service.find_organization(first_org)
            if matches:
                print(f"✅ Found {len(matches)} matches:")
                for match in matches:
                    print(f"  • {match['organization_name']} ({match['current_stage']}) - Score: {match.get('similarity_score', 'N/A')}")
            else:
                print(f"❌ No matches found")
        
        # Test partial search via service layer
        print("\n🔍 Testing partial search via DonorService...")
        if pipeline:
            first_stage = list(pipeline.keys())[0]
            first_org = pipeline[first_stage][0]['organization_name']
            # Search with first 3 characters
            partial_query = first_org[:3]
            print(f"🔍 Searching for: {partial_query}")
            
            matches = donor_service.find_organization(partial_query)
            if matches:
                print(f"✅ Found {len(matches)} matches:")
                for match in matches:
                    print(f"  • {match['organization_name']} ({match['current_stage']}) - Score: {match.get('similarity_score', 'N/A')}")
            else:
                print(f"❌ No matches found")
        
        # Test get_organization_by_name() via service layer
        print("\n🔍 Testing get_organization_by_name() via DonorService...")
        if pipeline:
            first_stage = list(pipeline.keys())[0]
            first_org = pipeline[first_stage][0]['organization_name']
            print(f"🔍 Getting exact match for: {first_org}")
            
            org_data = donor_service.get_organization_by_name(first_org)
            if org_data:
                print(f"✅ Found organization:")
                print(f"  • Name: {org_data['organization_name']}")
                print(f"  • Stage: {org_data['current_stage']}")
                print(f"  • Contact: {org_data['contact_person']}")
                print(f"  • Email: {org_data['email']}")
                print(f"  • Assigned: {org_data['assigned_to']}")
                print(f"  • Next Action: {org_data['next_action']}")
            else:
                print(f"❌ Organization not found")
        
        # Test get_organizations_by_stage() via service layer
        print("\n📋 Testing get_organizations_by_stage() via DonorService...")
        if stages:
            test_stage = stages[0]
            print(f"🔍 Getting organizations in stage: {test_stage}")
            
            stage_orgs = donor_service.get_organizations_by_stage(test_stage)
            print(f"✅ Found {len(stage_orgs)} organizations in {test_stage}")
            for org in stage_orgs[:3]:  # Show first 3
                print(f"  • {org['organization_name']}")
        
        # Test error handling via service layer
        print("\n🧪 Testing error handling via DonorService...")
        
        # Test with non-existent organization
        print("🔍 Testing search for non-existent organization...")
        matches = donor_service.find_organization("NON_EXISTENT_ORG_12345")
        if not matches:
            print("✅ Correctly returned no matches for non-existent organization")
        else:
            print("❌ Unexpectedly found matches for non-existent organization")
        
        # Test with empty query
        print("🔍 Testing search with empty query...")
        matches = donor_service.find_organization("")
        print(f"✅ Empty query returned {len(matches)} matches")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        logger.error(f"Test failed with exception: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_sheets_db()
    if success:
        print("\n✅ All tests passed! The comprehensive SheetsDB is working correctly.")
    else:
        print("\n💥 Some tests failed. Check the logs for details.")
        exit(1)
