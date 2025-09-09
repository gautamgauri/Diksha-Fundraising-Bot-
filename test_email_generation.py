#!/usr/bin/env python3
"""
Test Email Generation Functionality via Shared Backend
Diksha Foundation Fundraising Bot
"""

import requests
import json
import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration
BASE_URL = "http://localhost:5000"  # Flask app URL

def test_health():
    """Test basic health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_templates():
    """Test template listing endpoint"""
    print("\n📋 Testing template listing...")
    try:
        response = requests.get(f"{BASE_URL}/api/templates")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Templates endpoint working")
            templates = data.get('templates', {})
            print(f"📧 Available templates: {len(templates)}")
            for template_id, template_name in templates.items():
                print(f"   • {template_id}: {template_name}")
            return True
        else:
            print(f"❌ Templates endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Templates endpoint error: {e}")
        return False

def test_email_generation():
    """Test email generation via shared backend"""
    print("\n📧 Testing email generation via shared backend...")
    
    try:
        from backend import backend_manager
        
        if not backend_manager.initialized:
            print("❌ BackendManager not initialized")
            return
        
        email_service = backend_manager.email_service
        if not email_service:
            print("❌ EmailService not available")
            return
        
        # Test data
        test_cases = [
            {
                "org": "Wipro Foundation",
                "template": "identification",
                "description": "Initial outreach to Wipro"
            },
            {
                "org": "Tata Trust",
                "template": "engagement", 
                "description": "Relationship building with Tata"
            },
            {
                "org": "HDFC Bank",
                "template": "proposal",
                "description": "Formal proposal for HDFC"
            }
        ]
        
        for test_case in test_cases:
            print(f"\n🔍 Testing: {test_case['description']}")
            try:
                email_data = email_service.generate_email(
                    test_case["org"], 
                    test_case["template"]
                )
                
                if email_data:
                    print(f"✅ Email generated successfully via shared backend")
                    print(f"   📧 Subject: {email_data.get('subject', 'N/A')}")
                    print(f"   👤 Recipient: {email_data.get('recipient', 'N/A')}")
                    print(f"   📝 Body length: {len(email_data.get('body', ''))} characters")
                    print(f"   🏷️ Template: {email_data.get('template_type', 'N/A')}")
                else:
                    print(f"⚠️ Email generation failed (no test data available)")
                    
            except Exception as e:
                print(f"⚠️ Email generation error (expected if no test data): {e}")
        
        # Test API endpoint if Flask app is running
        print(f"\n🌐 Testing API endpoint...")
        try:
            response = requests.post(
                f"{BASE_URL}/api/generate-email",
                json={"org": "Wipro Foundation", "template": "identification"},
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API endpoint working")
                print(f"   📧 Subject: {data.get('subject', 'N/A')}")
                print(f"   🏷️ Template: {data.get('template_type', 'N/A')}")
            else:
                print(f"⚠️ API endpoint returned {response.status_code} (app may not be running)")
        except requests.exceptions.ConnectionError:
            print("⚠️ Flask app not running - skipping API endpoint test")
        except Exception as e:
            print(f"⚠️ API endpoint test failed: {e}")
                    
    except Exception as e:
        print(f"❌ Email generation test failed: {e}")

def test_slack_command_simulation():
    """Simulate Slack command behavior via shared backend"""
    print("\n🤖 Testing Slack command simulation via shared backend...")
    
    try:
        from backend import backend_manager
        
        if not backend_manager.initialized:
            print("❌ BackendManager not initialized")
            return
        
        donor_service = backend_manager.donor_service
        email_service = backend_manager.email_service
        
        if not donor_service or not email_service:
            print("❌ Required services not available")
            return
        
        # Test the same functionality that Slack would use
        test_org = "Wipro Foundation"
        test_template = "identification"
        
        print(f"🔍 Simulating: /donoremail {test_template} {test_org}")
        
        # First get organization status via shared backend
        matches = donor_service.find_organization(test_org)
        if matches:
            org_data = matches[0]
            print(f"✅ Found organization via shared backend: {org_data['organization_name']}")
            print(f"   📊 Stage: {org_data['current_stage']}")
            print(f"   👤 Contact: {org_data['contact_person']}")
            print(f"   📧 Email: {org_data['email']}")
            
            # Now generate email via shared backend
            try:
                email_data = email_service.generate_email(test_org, test_template)
                if email_data:
                    print(f"\n📧 Email generated via shared backend:")
                    print(f"   Subject: {email_data.get('subject', 'N/A')}")
                    print(f"   Template: {email_data.get('template_type', 'N/A')}")
                    print(f"   Recipient: {email_data.get('recipient', 'N/A')}")
                else:
                    print(f"⚠️ Email generation failed (no test data available)")
            except Exception as e:
                print(f"⚠️ Email generation failed: {e}")
                
        else:
            print(f"⚠️ Organization '{test_org}' not found (may not exist in data)")
            # Try with first available organization
            pipeline = donor_service.get_pipeline()
            if pipeline:
                first_stage = list(pipeline.keys())[0]
                first_org = pipeline[first_stage][0]['organization_name']
                print(f"🔍 Trying with first available organization: {first_org}")
                
                matches = donor_service.find_organization(first_org)
                if matches:
                    org_data = matches[0]
                    print(f"✅ Found test organization: {org_data['organization_name']}")
                    
                    try:
                        email_data = email_service.generate_email(first_org, test_template)
                        if email_data:
                            print(f"\n📧 Email generated via shared backend:")
                            print(f"   Subject: {email_data.get('subject', 'N/A')}")
                            print(f"   Template: {email_data.get('template_type', 'N/A')}")
                        else:
                            print(f"⚠️ Email generation failed (no test data available)")
                    except Exception as e:
                        print(f"⚠️ Email generation failed: {e}")
            
    except Exception as e:
        print(f"❌ Slack simulation error: {e}")

def main():
    """Run all tests via shared backend"""
    print("🚀 Diksha Foundation Email Generation Test Suite")
    print("Testing via Shared Backend Architecture")
    print("=" * 50)
    
    # Test basic connectivity
    if not test_health():
        print("\n❌ Basic connectivity failed. Check if the server is running.")
        sys.exit(1)
    
    # Test template system
    if not test_templates():
        print("\n❌ Template system failed.")
        sys.exit(1)
    
    # Test email generation
    test_email_generation()
    
    # Test Slack command simulation
    test_slack_command_simulation()
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")
    print("\n💡 Next steps:")
    print("1. Run: python app_refactored.py (to test Web UI)")
    print("2. Run: python slack_bot_refactored.py (to test Slack)")
    print("3. Test in Slack: /donoremail identification Wipro Foundation")
    print("4. Use API: POST /api/generate-email with org and template")
    print("5. Both interfaces now use the same shared backend!")

if __name__ == "__main__":
    main()

