#!/usr/bin/env python3
"""
Test Email Generation Functionality
Diksha Foundation Fundraising Bot
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:3000"  # Change this to your Railway URL when deployed

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
        response = requests.get(f"{BASE_URL}/debug/templates")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Templates endpoint working")
            print(f"📧 Available templates: {data['template_count']}")
            for template_id, template_name in data['available_templates'].items():
                print(f"   • {template_id}: {template_name}")
            return True
        else:
            print(f"❌ Templates endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Templates endpoint error: {e}")
        return False

def test_email_generation():
    """Test email generation endpoint"""
    print("\n📧 Testing email generation...")
    
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
            payload = {
                "org": test_case["org"],
                "template": test_case["template"]
            }
            
            response = requests.post(
                f"{BASE_URL}/debug/generate-email",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Email generated successfully")
                print(f"   📧 Subject: {data['email']['subject']}")
                print(f"   👤 Recipient: {data['email']['recipient']}")
                print(f"   📝 Body length: {len(data['email']['body'])} characters")
                print(f"   🏷️ Template: {data['template_type']}")
            else:
                print(f"❌ Email generation failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Response: {response.text}")
                    
        except Exception as e:
            print(f"❌ Email generation error: {e}")

def test_slack_command_simulation():
    """Simulate Slack command behavior"""
    print("\n🤖 Testing Slack command simulation...")
    
    # Test the same functionality that Slack would use
    test_org = "Wipro Foundation"
    test_template = "identification"
    
    print(f"🔍 Simulating: /pipeline email {test_org} | {test_template}")
    
    try:
        # First get organization status
        status_response = requests.get(f"{BASE_URL}/debug/status?org={test_org}")
        if status_response.status_code == 200:
            org_data = status_response.json()
            print(f"✅ Found organization: {org_data['organization']}")
            print(f"   📊 Stage: {org_data['stage']}")
            print(f"   👤 Contact: {org_data['contact_person']}")
            print(f"   📧 Email: {org_data['email']}")
            
            # Now generate email
            email_response = requests.post(
                f"{BASE_URL}/debug/generate-email",
                json={"org": test_org, "template": test_template},
                headers={"Content-Type": "application/json"}
            )
            
            if email_response.status_code == 200:
                email_data = email_response.json()
                print(f"\n📧 Email generated via API:")
                print(f"   Subject: {email_data['email']['subject']}")
                print(f"   Template: {email_data['template_type']}")
                print(f"   Context: {email_data['donor_context']['sector']} in {email_data['donor_context']['geography']}")
            else:
                print(f"❌ Email generation failed")
                
        else:
            print(f"❌ Organization lookup failed: {status_response.status_code}")
            
    except Exception as e:
        print(f"❌ Slack simulation error: {e}")

def main():
    """Run all tests"""
    print("🚀 Diksha Foundation Email Generation Test Suite")
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
    print("1. Deploy to Railway: git push origin main")
    print("2. Test in Slack: /pipeline email Wipro Foundation | identification")
    print("3. Use API: POST /debug/generate-email with org and template")

if __name__ == "__main__":
    main()
