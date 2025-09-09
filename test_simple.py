#!/usr/bin/env python3
"""
Simple test script for the simplified SheetsDB implementation
"""

from backend import backend_manager

def test_sheets_db():
    """Test the simplified SheetsDB implementation via shared backend"""
    print("🔍 Testing Simplified SheetsDB via Shared Backend...")
    
    try:
        # Initialize via BackendManager
        if not backend_manager.initialized:
            print("❌ BackendManager not initialized")
            return
        
        donor_service = backend_manager.donor_service
        if not donor_service:
            print("❌ DonorService not available")
            return
        
        print(f"✅ BackendManager initialized")
        print(f"📊 Using shared backend services")
        
        # Test get_pipeline() via service
        print("\n📋 Testing get_pipeline() via DonorService...")
        pipeline = donor_service.get_pipeline()
        print(f"✅ Retrieved {len(pipeline)} stages:")
        for stage, orgs in pipeline.items():
            print(f"  • {stage}: {len(orgs)} organizations")
        
        # Test find_organization() via service
        print("\n🔍 Testing find_organization() via DonorService...")
        # Try to find a sample organization
        if pipeline:
            # Get first organization from first stage
            first_stage = list(pipeline.keys())[0]
            first_org = pipeline[first_stage][0]['organization_name']
            print(f"🔍 Searching for: {first_org}")
            
            matches = donor_service.find_organization(first_org)
            if matches:
                result = matches[0]  # Get first match
                print(f"✅ Found: {result['organization_name']} ({result['current_stage']})")
                print(f"   Contact: {result['contact_person']}")
                print(f"   Email: {result['email']}")
            else:
                print(f"❌ Not found")
        
        # Test search with partial name via service
        print("\n🔍 Testing partial search via DonorService...")
        if pipeline:
            first_stage = list(pipeline.keys())[0]
            first_org = pipeline[first_stage][0]['organization_name']
            # Search with first 3 characters
            partial_query = first_org[:3]
            print(f"🔍 Searching for: {partial_query}")
            
            matches = donor_service.find_organization(partial_query)
            if matches:
                result = matches[0]  # Get first match
                print(f"✅ Found: {result['organization_name']} ({result['current_stage']})")
            else:
                print(f"❌ Not found")
        
        print("\n🎉 All tests completed via shared backend!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sheets_db()

