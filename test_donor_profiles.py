#!/usr/bin/env python3
"""
Test Donor Profile Integration
Diksha Foundation Fundraising Bot
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:3000"  # Change this to your Railway URL when deployed

def test_donor_profile_endpoint():
    """Test the donor profile endpoint"""
    print("📁 Testing Donor Profile Endpoint")
    print("=" * 50)
    
    test_organizations = [
        "Wipro Foundation",
        "Tata Trust",
        "HDFC Bank",
        "Test Organization"
    ]
    
    for org in test_organizations:
        print(f"\n🔍 Testing: {org}")
        
        try:
            response = requests.get(
                f"{BASE_URL}/debug/donor-profile",
                params={"org": org}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('ok'):
                    if data.get('profile_found'):
                        print(f"   ✅ Profile found")
                        file_info = data.get('file_info', {})
                        print(f"   📄 File: {file_info.get('name', 'N/A')}")
                        print(f"   📋 Type: {file_info.get('type', 'N/A')}")
                        print(f"   📅 Modified: {file_info.get('modified', 'N/A')}")
                        print(f"   🔗 Web Link: {file_info.get('web_link', 'N/A')}")
                        print(f"   📝 Content Length: {data.get('content_length', 'N/A')} characters")
                        
                        # Show content summary
                        summary = data.get('content_summary', '')
                        if summary:
                            print(f"   📋 Summary: {summary[:100]}...")
                    else:
                        print(f"   ⚠️  No profile found")
                        print(f"   💬 Message: {data.get('message', 'N/A')}")
                    
                    print(f"   🔧 Drive Service: {data.get('drive_service', 'N/A')}")
                else:
                    print(f"   ❌ Error: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"      Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"      Response: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Request Error: {e}")

def test_email_with_profiles():
    """Test email generation with donor profiles"""
    print("\n📧 Testing Email Generation with Donor Profiles")
    print("=" * 50)
    
    test_cases = [
        {
            "org": "Wipro Foundation",
            "template": "identification",
            "description": "Initial outreach with profile data"
        },
        {
            "org": "Tata Trust",
            "template": "engagement",
            "description": "Relationship building with profile data"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['description']}")
        print(f"   Organization: {test_case['org']}")
        print(f"   Template: {test_case['template']}")
        
        try:
            # First check if profile exists
            profile_response = requests.get(
                f"{BASE_URL}/debug/donor-profile",
                params={"org": test_case["org"]}
            )
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                if profile_data.get('profile_found'):
                    print(f"   📁 Profile: ✅ Available")
                    
                    # Now test email generation
                    email_response = requests.post(
                        f"{BASE_URL}/debug/generate-email",
                        json={
                            "org": test_case["org"],
                            "template": test_case["template"],
                            "mode": "claude"
                        },
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if email_response.status_code == 200:
                        email_data = email_response.json()
                        print(f"   📧 Email: ✅ Generated")
                        print(f"   🤖 Mode: {email_data.get('email', {}).get('mode', 'N/A')}")
                        print(f"   📝 Subject: {email_data.get('email', {}).get('subject', 'N/A')}")
                        print(f"   📏 Body Length: {len(email_data.get('email', {}).get('body', ''))} characters")
                        
                        # Check if profile data was used
                        body = email_data.get('email', {}).get('body', '').lower()
                        if 'profile' in body or 'mission' in body or 'programs' in body:
                            print(f"   🎯 Profile Integration: ✅ Detected in email")
                        else:
                            print(f"   🎯 Profile Integration: ⚠️  Not clearly visible")
                    else:
                        print(f"   📧 Email: ❌ Failed ({email_response.status_code})")
                else:
                    print(f"   📁 Profile: ❌ Not found")
                    print(f"   💬 Message: {profile_data.get('message', 'N/A')}")
            else:
                print(f"   📁 Profile Check: ❌ Failed ({profile_response.status_code})")
                
        except Exception as e:
            print(f"   ❌ Test Error: {e}")

def test_profile_comparison():
    """Test template comparison with profile data"""
    print("\n🔍 Testing Template Comparison with Profiles")
    print("=" * 50)
    
    test_org = "Wipro Foundation"
    test_template = "identification"
    
    try:
        print(f"🔍 Testing: {test_org} | {test_template}")
        
        response = requests.get(
            f"{BASE_URL}/debug/compare-templates",
            params={
                "org": test_org,
                "template": test_template
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('ok'):
                print(f"   ✅ Comparison successful")
                
                # Check if profile data was used in enhancement
                enhanced_body = data.get('comparison', {}).get('enhanced_template', {}).get('body', '')
                if enhanced_body:
                    enhanced_lower = enhanced_body.lower()
                    
                    profile_indicators = [
                        'profile', 'mission', 'vision', 'programs', 'initiatives',
                        'partnerships', 'impact', 'geographic', 'sector', 'target'
                    ]
                    
                    found_indicators = []
                    for indicator in profile_indicators:
                        if indicator in enhanced_lower:
                            found_indicators.append(indicator)
                    
                    if found_indicators:
                        print(f"   🎯 Profile Integration: ✅ Detected indicators: {', '.join(found_indicators)}")
                    else:
                        print(f"   🎯 Profile Integration: ⚠️  No clear profile indicators found")
                
                # Show enhancement metrics
                metrics = data.get('comparison', {}).get('enhancement_metrics', {})
                print(f"   📊 Similarity: {metrics.get('similarity_score', 'N/A')}")
                print(f"   📈 Improvement: {metrics.get('improvement_percentage', 'N/A')}%")
                print(f"   📏 Length Change: {metrics.get('length_change', 'N/A')} characters")
                
            else:
                print(f"   ❌ Comparison failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test Error: {e}")

def main():
    """Run all donor profile tests"""
    print("🚀 Diksha Foundation Donor Profile Integration Test Suite")
    print("=" * 60)
    
    # Test donor profile endpoint
    test_donor_profile_endpoint()
    
    # Test email generation with profiles
    test_email_with_profiles()
    
    # Test template comparison with profiles
    test_profile_comparison()
    
    print("\n" + "=" * 60)
    print("✅ Donor Profile Integration Test Suite Completed!")
    print("\n💡 Key Benefits of Profile Integration:")
    print("1. 📁 Reads donor profiles from Google Drive")
    print("2. 🎯 Uses profile data to personalize emails")
    print("3. 🤖 Claude gets rich context for better enhancement")
    print("4. 📊 Fallback to Sheets data if profiles unavailable")
    print("5. 🔍 Smart profile content extraction and summarization")
    print("\n🌐 Test endpoints:")
    print(f"   • Donor Profile: {BASE_URL}/debug/donor-profile?org=Wipro Foundation")
    print(f"   • Email Generation: {BASE_URL}/debug/generate-email")
    print(f"   • Template Comparison: {BASE_URL}/debug/compare-templates?org=Wipro Foundation&template=identification")

if __name__ == "__main__":
    main()

