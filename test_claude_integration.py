#!/usr/bin/env python3
"""
Test Claude Integration for Email Generation
Diksha Foundation Fundraising Bot
"""

import requests
import json
import sys
import os

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

def test_claude_integration():
    """Test Claude API integration"""
    print("\n🤖 Testing Claude API integration...")
    try:
        response = requests.get(f"{BASE_URL}/debug/test-claude")
        if response.status_code == 200:
            data = response.json()
            print("✅ Claude test endpoint working")
            
            # Check API key status
            api_status = data.get('claude_api_key', 'unknown')
            print(f"🔑 Claude API Key: {api_status}")
            
            # Check Claude mode results
            claude_status = data.get('claude_mode', {}).get('status', 'unknown')
            claude_subject = data.get('claude_mode', {}).get('subject', 'N/A')
            claude_length = data.get('claude_mode', {}).get('body_length', 0)
            
            print(f"🤖 Claude Mode: {claude_status}")
            if claude_status == 'working':
                print(f"   📧 Subject: {claude_subject}")
                print(f"   📝 Body Length: {claude_length} characters")
            else:
                print("   ❌ Claude mode failed")
            
            # Check template mode results
            template_status = data.get('template_mode', {}).get('status', 'unknown')
            template_subject = data.get('template_mode', {}).get('subject', 'N/A')
            template_length = data.get('template_mode', {}).get('body_length', 0)
            
            print(f"📋 Template Mode: {template_status}")
            if template_status == 'working':
                print(f"   📧 Subject: {template_subject}")
                print(f"   📝 Body Length: {template_length} characters")
            else:
                print("   ❌ Template mode failed")
            
            return True
        else:
            print(f"❌ Claude test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Claude test error: {e}")
        return False

def test_email_generation_modes():
    """Test email generation in both modes"""
    print("\n📧 Testing email generation modes...")
    
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
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['description']}")
        
        # Test Claude mode
        print("   🤖 Testing Claude mode...")
        claude_response = requests.post(
            f"{BASE_URL}/debug/generate-email",
            json={
                "org": test_case["org"],
                "template": test_case["template"],
                "mode": "claude"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if claude_response.status_code == 200:
            claude_data = claude_response.json()
            print(f"     ✅ Claude mode working")
            print(f"     📧 Subject: {claude_data['email']['subject']}")
            print(f"     📝 Body length: {len(claude_data['email']['body'])} characters")
        else:
            print(f"     ❌ Claude mode failed: {claude_response.status_code}")
        
        # Test template mode
        print("   📋 Testing template mode...")
        template_response = requests.post(
            f"{BASE_URL}/debug/generate-email",
            json={
                "org": test_case["org"],
                "template": test_case["template"],
                "mode": "template"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if template_response.status_code == 200:
            template_data = template_response.json()
            print(f"     ✅ Template mode working")
            print(f"     📧 Subject: {template_data['email']['subject']}")
            print(f"     📝 Body length: {len(template_data['email']['body'])} characters")
        else:
            print(f"     ❌ Template mode failed: {template_response.status_code}")

def test_slack_commands():
    """Test Slack command simulation"""
    print("\n🤖 Testing Slack command simulation...")
    
    # Test mode command
    print("   🔧 Testing mode command...")
    mode_response = requests.get(f"{BASE_URL}/debug/status?org=Wipro Foundation")
    if mode_response.status_code == 200:
        print("     ✅ Organization lookup working")
        
        # Test email generation with mode
        email_response = requests.post(
            f"{BASE_URL}/debug/generate-email",
            json={
                "org": "Wipro Foundation",
                "template": "identification",
                "mode": "claude"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if email_response.status_code == 200:
            print("     ✅ Email generation with mode working")
        else:
            print("     ❌ Email generation with mode failed")
    else:
        print("     ❌ Organization lookup failed")

def main():
    """Run all tests"""
    print("🚀 Diksha Foundation Claude Integration Test Suite")
    print("=" * 60)
    
    # Check environment
    claude_key = os.environ.get("ANTHROPIC_API_KEY")
    if claude_key:
        print(f"🔑 Claude API Key: Configured ({claude_key[:10]}...)")
    else:
        print("⚠️  Claude API Key: Not configured")
        print("   Set ANTHROPIC_API_KEY environment variable for full functionality")
    
    print()
    
    # Test basic connectivity
    if not test_health():
        print("\n❌ Basic connectivity failed. Check if the server is running.")
        sys.exit(1)
    
    # Test Claude integration
    test_claude_integration()
    
    # Test email generation modes
    test_email_generation_modes()
    
    # Test Slack commands
    test_slack_commands()
    
    print("\n" + "=" * 60)
    print("✅ Claude integration test suite completed!")
    print("\n💡 Next steps:")
    print("1. Deploy to Railway: git push origin main")
    print("2. Set ANTHROPIC_API_KEY in Railway environment variables")
    print("3. Test in Slack: /pipeline email Wipro Foundation | identification | claude")
    print("4. Compare modes: /pipeline email Wipro Foundation | identification | template")

if __name__ == "__main__":
    main()

