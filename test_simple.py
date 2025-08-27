#!/usr/bin/env python3
"""
Simple test script for the simplified SheetsDB implementation
"""

from app.modules.sheets_sync import SheetsDB

def test_sheets_db():
    """Test the simplified SheetsDB implementation"""
    print("🔍 Testing Simplified SheetsDB...")
    
    try:
        # Initialize SheetsDB
        db = SheetsDB()
        print(f"✅ SheetsDB initialized")
        print(f"📊 Sheet ID: {db.sheet_id}")
        print(f"📋 Tab: {db.tab}")
        
        # Test get_pipeline()
        print("\n📋 Testing get_pipeline()...")
        pipeline = db.get_pipeline()
        print(f"✅ Retrieved {len(pipeline)} stages:")
        for stage, orgs in pipeline.items():
            print(f"  • {stage}: {len(orgs)} organizations")
        
        # Test find_org()
        print("\n🔍 Testing find_org()...")
        # Try to find a sample organization
        if pipeline:
            # Get first organization from first stage
            first_stage = list(pipeline.keys())[0]
            first_org = pipeline[first_stage][0]['organization']
            print(f"🔍 Searching for: {first_org}")
            
            result = db.find_org(first_org)
            if result:
                print(f"✅ Found: {result['organization']} ({result['stage']})")
                print(f"   Contact: {result['contact']}")
                print(f"   Email: {result['email']}")
            else:
                print(f"❌ Not found")
        
        # Test search with partial name
        print("\n🔍 Testing partial search...")
        if pipeline:
            first_stage = list(pipeline.keys())[0]
            first_org = pipeline[first_stage][0]['organization']
            # Search with first 3 characters
            partial_query = first_org[:3]
            print(f"🔍 Searching for: {partial_query}")
            
            result = db.find_org(partial_query)
            if result:
                print(f"✅ Found: {result['organization']} ({result['stage']})")
            else:
                print(f"❌ Not found")
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sheets_db()

