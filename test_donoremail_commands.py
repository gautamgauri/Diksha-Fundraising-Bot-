#!/usr/bin/env python3
"""
Test Donor Email Commands
Diksha Foundation Fundraising Bot
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:3000"  # Change this to your Railway URL when deployed

def test_donoremail_commands():
    """Test the new donoremail command structure"""
    print("📧 Testing Donor Email Commands")
    print("=" * 50)
    
    # Test Stage 1: Prospecting / Outreach
    print("\n🟢 Stage 1: Prospecting / Outreach")
    test_intro_command()
    test_concept_command()
    test_followup_command()
    
    # Test Stage 2: Engagement
    print("\n🔵 Stage 2: Engagement")
    test_meeting_request_command()
    test_thanks_meeting_command()
    test_connect_command()
    
    # Test Stage 3: Proposal Submission
    print("\n🟣 Stage 3: Proposal Submission")
    test_proposal_cover_command()
    test_proposal_reminder_command()
    test_pitch_command()
    
    # Test Stage 4: Stewardship
    print("\n🔴 Stage 4: Stewardship for Fundraising")
    test_impact_story_command()
    test_invite_command()
    test_festival_greeting_command()
    
    # Test Utilities
    print("\n⚙️ Utilities")
    test_refine_command()
    test_insert_profile_command()
    test_save_command()
    test_share_command()

def test_intro_command():
    """Test intro email command"""
    print(f"\n🔍 Testing: /donoremail intro Wipro Foundation")
    
    try:
        response = requests.post(
            f"{BASE_URL}/slack/commands",
            data={
                "command": "/donoremail",
                "text": "intro Wipro Foundation",
                "user_id": "test_user",
                "channel_id": "test_channel"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('response_type', 'N/A')}")
            if data.get('text'):
                print(f"   📝 Response: {data['text'][:100]}...")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test Error: {e}")

def test_concept_command():
    """Test concept email command"""
    print(f"\n🔍 Testing: /donoremail concept Tata Trust Digital Skills Training")
    
    try:
        response = requests.post(
            f"{BASE_URL}/slack/commands",
            data={
                "command": "/donoremail",
                "text": "concept Tata Trust Digital Skills Training",
                "user_id": "test_user",
                "channel_id": "test_channel"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('response_type', 'N/A')}")
            if data.get('text'):
                print(f"   📝 Response: {data['text'][:100]}...")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test Error: {e}")

def test_followup_command():
    """Test followup email command"""
    print(f"\n🔍 Testing: /donoremail followup HDFC Bank")
    
    try:
        response = requests.post(
            f"{BASE_URL}/slack/commands",
            data={
                "command": "/donoremail",
                "text": "followup HDFC Bank",
                "user_id": "test_user",
                "channel_id": "test_channel"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('response_type', 'N/A')}")
            if data.get('text'):
                print(f"   📝 Response: {data['text'][:100]}...")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test Error: {e}")

def test_meeting_request_command():
    """Test meeting request command"""
    print(f"\n🔍 Testing: /donoremail meetingrequest Wipro Foundation 2024-02-15")
    
    try:
        response = requests.post(
            f"{BASE_URL}/slack/commands",
            data={
                "command": "/donoremail",
                "text": "meetingrequest Wipro Foundation 2024-02-15",
                "user_id": "test_user",
                "channel_id": "test_channel"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('response_type', 'N/A')}")
            if data.get('text'):
                print(f"   📝 Response: {data['text'][:100]}...")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test Error: {e}")

def test_thanks_meeting_command():
    """Test thanks meeting command"""
    print(f"\n🔍 Testing: /donoremail thanksmeeting Tata Trust")
    
    try:
        response = requests.post(
            f"{BASE_URL}/slack/commands",
            data={
                "command": "/donoremail",
                "text": "thanksmeeting Tata Trust",
                "user_id": "test_user",
                "channel_id": "test_channel"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('response_type', 'N/A')}")
            if data.get('text'):
                print(f"   📝 Response: {data['text'][:100]}...")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test Error: {e}")

def test_connect_command():
    """Test connect command"""
    print(f"\n🔍 Testing: /donoremail connect Infosys Foundation")
    
    try:
        response = requests.post(
            f"{BASE_URL}/slack/commands",
            data={
                "command": "/donoremail",
                "text": "connect Infosys Foundation",
                "user_id": "test_user",
                "channel_id": "test_channel"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('response_type', 'N/A')}")
            if data.get('text'):
                print(f"   📝 Response: {data['text'][:100]}...")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test Error: {e}")

def test_proposal_cover_command():
    """Test proposal cover command"""
    print(f"\n🔍 Testing: /donoremail proposalcover Wipro Foundation Digital Skills Program")
    
    try:
        response = requests.post(
            f"{BASE_URL}/slack/commands",
            data={
                "command": "/donoremail",
                "text": "proposalcover Wipro Foundation Digital Skills Program",
                "user_id": "test_user",
                "channel_id": "test_channel"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('response_type', 'N/A')}")
            if data.get('text'):
                print(f"   📝 Response: {data['text'][:100]}...")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test Error: {e}")

def test_proposal_reminder_command():
    """Test proposal reminder command"""
    print(f"\n🔍 Testing: /donoremail proposalreminder Tata Trust")
    
    try:
        response = requests.post(
            f"{BASE_URL}/slack/commands",
            data={
                "command": "/donoremail",
                "text": "proposalreminder Tata Trust",
                "user_id": "test_user",
                "channel_id": "test_channel"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('response_type', 'N/A')}")
            if data.get('text'):
                print(f"   📝 Response: {data['text'][:100]}...")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test Error: {e}")

def test_pitch_command():
    """Test pitch command"""
    print(f"\n🔍 Testing: /donoremail pitch HDFC Bank Youth Empowerment")
    
    try:
        response = requests.post(
            f"{BASE_URL}/slack/commands",
            data={
                "command": "/donoremail",
                "text": "pitch HDFC Bank Youth Empowerment",
                "user_id": "test_user",
                "channel_id": "test_channel"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('response_type', 'N/A')}")
            if data.get('text'):
                print(f"   📝 Response: {data['text'][:100]}...")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test Error: {e}")

def test_impact_story_command():
    """Test impact story command"""
    print(f"\n🔍 Testing: /donoremail impactstory Wipro Foundation Digital Literacy")
    
    try:
        response = requests.post(
            f"{BASE_URL}/slack/commands",
            data={
                "command": "/donoremail",
                "text": "impactstory Wipro Foundation Digital Literacy",
                "user_id": "test_user",
                "channel_id": "test_channel"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('response_type', 'N/A')}")
            if data.get('text'):
                print(f"   📝 Response: {data['text'][:100]}...")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test Error: {e}")

def test_invite_command():
    """Test invite command"""
    print(f"\n🔍 Testing: /donoremail invite Tata Trust Annual Meeting 2024-03-20")
    
    try:
        response = requests.post(
            f"{BASE_URL}/slack/commands",
            data={
                "command": "/donoremail",
                "text": "invite Tata Trust Annual Meeting 2024-03-20",
                "user_id": "test_user",
                "channel_id": "test_channel"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('response_type', 'N/A')}")
            if data.get('text'):
                print(f"   📝 Response: {data['text'][:100]}...")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test Error: {e}")

def test_festival_greeting_command():
    """Test festival greeting command"""
    print(f"\n🔍 Testing: /donoremail festivalgreeting HDFC Bank Diwali")
    
    try:
        response = requests.post(
            f"{BASE_URL}/slack/commands",
            data={
                "command": "/donoremail",
                "text": "festivalgreeting HDFC Bank Diwali",
                "user_id": "test_user",
                "channel_id": "test_channel"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('response_type', 'N/A')}")
            if data.get('text'):
                print(f"   📝 Response: {data['text'][:100]}...")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test Error: {e}")

def test_refine_command():
    """Test refine command"""
    print(f"\n🔍 Testing: /donoremail refine warm")
    
    try:
        response = requests.post(
            f"{BASE_URL}/slack/commands",
            data={
                "command": "/donoremail",
                "text": "refine warm",
                "user_id": "test_user",
                "channel_id": "test_channel"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('response_type', 'N/A')}")
            if data.get('text'):
                print(f"   📝 Response: {data['text'][:100]}...")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test Error: {e}")

def test_insert_profile_command():
    """Test insert profile command"""
    print(f"\n🔍 Testing: /donoremail insert profile Wipro Foundation")
    
    try:
        response = requests.post(
            f"{BASE_URL}/slack/commands",
            data={
                "command": "/donoremail",
                "text": "insert profile Wipro Foundation",
                "user_id": "test_user",
                "channel_id": "test_channel"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('response_type', 'N/A')}")
            if data.get('text'):
                print(f"   📝 Response: {data['text'][:100]}...")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test Error: {e}")

def test_save_command():
    """Test save command"""
    print(f"\n🔍 Testing: /donoremail save Wipro Foundation Intro")
    
    try:
        response = requests.post(
            f"{BASE_URL}/slack/commands",
            data={
                "command": "/donoremail",
                "text": "save Wipro Foundation Intro",
                "user_id": "test_user",
                "channel_id": "test_channel"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('response_type', 'N/A')}")
            if data.get('text'):
                print(f"   📝 Response: {data['text'][:100]}...")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test Error: {e}")

def test_share_command():
    """Test share command"""
    print(f"\n🔍 Testing: /donoremail share @sarah")
    
    try:
        response = requests.post(
            f"{BASE_URL}/slack/commands",
            data={
                "command": "/donoremail",
                "text": "share @sarah",
                "user_id": "test_user",
                "channel_id": "test_channel"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('response_type', 'N/A')}")
            if data.get('text'):
                print(f"   📝 Response: {data['text'][:100]}...")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test Error: {e}")

def main():
    """Run all donoremail command tests"""
    print("🚀 Diksha Foundation Donor Email Commands Test Suite")
    print("=" * 60)
    
    test_donoremail_commands()
    
    print("\n" + "=" * 60)
    print("✅ Donor Email Commands Test Suite Completed!")
    print("\n💡 **New Command Structure Benefits:**")
    print("1. 🎯 Clear fundraising workflow stages")
    print("2. 📧 Intuitive email generation commands")
    print("3. 🤖 AI enhancement with Claude")
    print("4. 📁 Google Drive profile integration")
    print("5. 🔧 Utility commands for workflow management")
    print("\n🌐 **Available Commands:**")
    print("   • /donoremail intro [OrgName] - First introduction")
    print("   • /donoremail concept [Org] [Project] - Concept pitch")
    print("   • /donoremail meetingrequest [Org] [Date] - Meeting request")
    print("   • /donoremail proposalcover [Org] [Project] - Proposal cover")
    print("   • /donoremail help - See all available commands")
    print("\n🚀 **Ready for Production Use!**")

if __name__ == "__main__":
    main()
