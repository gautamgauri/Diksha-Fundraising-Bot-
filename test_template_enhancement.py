#!/usr/bin/env python3
"""
Test Template Enhancement Comparison
Diksha Foundation Fundraising Bot
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:3000"  # Change this to your Railway URL when deployed

def test_template_comparison():
    """Test template enhancement comparison"""
    print("🔍 Testing template enhancement comparison...")
    
    test_cases = [
        {
            "org": "Wipro Foundation",
            "template": "identification",
            "description": "Initial outreach template enhancement"
        },
        {
            "org": "Tata Trust",
            "template": "engagement",
            "description": "Relationship building template enhancement"
        },
        {
            "org": "HDFC Bank",
            "template": "proposal",
            "description": "Proposal template enhancement"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📧 Testing: {test_case['description']}")
        print(f"   Organization: {test_case['org']}")
        print(f"   Template: {test_case['template']}")
        
        try:
            # Test template comparison
            response = requests.get(
                f"{BASE_URL}/debug/compare-templates",
                params={
                    "org": test_case["org"],
                    "template": test_case["template"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                comparison = data.get('comparison', {})
                metrics = comparison.get('enhancement_metrics', {})
                
                print(f"   ✅ Comparison successful")
                print(f"   📊 Similarity Score: {metrics.get('similarity_score', 'N/A')}")
                print(f"   📈 Improvement: {metrics.get('improvement_percentage', 'N/A')}%")
                print(f"   📏 Length Change: {metrics.get('length_change', 'N/A')} characters")
                
                # Show base vs enhanced
                base = comparison.get('base_template', {})
                enhanced = comparison.get('enhanced_template', {})
                
                print(f"   📋 Base Template Length: {base.get('total_length', 'N/A')}")
                print(f"   🤖 Enhanced Template Length: {enhanced.get('total_length', 'N/A')}")
                
                # Show subject line comparison
                print(f"   📧 Base Subject: {base.get('subject', 'N/A')}")
                print(f"   🚀 Enhanced Subject: {enhanced.get('subject', 'N/A')}")
                
            else:
                print(f"   ❌ Comparison failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"      Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"      Response: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Comparison error: {e}")

def test_enhancement_quality():
    """Test the quality of enhancements"""
    print("\n🎯 Testing enhancement quality...")
    
    # Test with a specific case
    test_org = "Wipro Foundation"
    test_template = "identification"
    
    try:
        response = requests.get(
            f"{BASE_URL}/debug/compare-templates",
            params={
                "org": test_org,
                "template": test_template
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            comparison = data.get('comparison', {})
            
            print(f"🔍 Enhancement Analysis for {test_org}")
            print(f"   Template Type: {test_template}")
            
            # Analyze enhancement quality
            base_text = f"{comparison['base_template']['subject']} {comparison['base_template']['body']}"
            enhanced_text = f"{comparison['enhanced_template']['subject']} {comparison['enhanced_template']['body']}"
            
            # Check for key improvements
            improvements = []
            if len(enhanced_text) > len(base_text):
                improvements.append("Longer, more detailed content")
            
            if "particularly relevant" in enhanced_text.lower():
                improvements.append("Sector-specific customization")
            
            if "exceptional alignment" in enhanced_text.lower():
                improvements.append("Alignment score enhancement")
            
            if "priority partnership" in enhanced_text.lower():
                improvements.append("Priority-based customization")
            
            print(f"   📈 Key Improvements:")
            if improvements:
                for improvement in improvements:
                    print(f"      ✅ {improvement}")
            else:
                print(f"      ⚠️  No significant improvements detected")
            
            # Show donor context
            donor_context = data.get('donor_context', {})
            print(f"   🏢 Donor Context:")
            print(f"      Sector: {donor_context.get('sector', 'N/A')}")
            print(f"      Geography: {donor_context.get('geography', 'N/A')}")
            print(f"      Alignment: {donor_context.get('alignment_score', 'N/A')}/10")
            print(f"      Priority: {donor_context.get('priority', 'N/A')}")
            
        else:
            print(f"❌ Enhancement quality test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Enhancement quality test error: {e}")

def main():
    """Run all tests"""
    print("🚀 Diksha Foundation Template Enhancement Test Suite")
    print("=" * 60)
    
    # Test template comparison
    test_template_comparison()
    
    # Test enhancement quality
    test_enhancement_quality()
    
    print("\n" + "=" * 60)
    print("✅ Template enhancement test suite completed!")
    print("\n💡 Key Benefits of Template-Based Enhancement:")
    print("1. 📋 Maintains your proven template structure")
    print("2. 🤖 AI enhances language and personalization")
    print("3. 🎯 Stage-specific improvements")
    print("4. 🔄 Automatic fallback to base templates")
    print("5. 📊 Quality metrics and comparison")
    print("\n🌐 Test endpoints:")
    print(f"   • Compare templates: {BASE_URL}/debug/compare-templates?org=Wipro Foundation&template=identification")
    print(f"   • Test Claude: {BASE_URL}/debug/test-claude")
    print(f"   • Available templates: {BASE_URL}/debug/templates")

if __name__ == "__main__":
    main()
