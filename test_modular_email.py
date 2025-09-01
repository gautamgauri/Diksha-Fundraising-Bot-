#!/usr/bin/env python3
"""
Test Modular Email Generator
Diksha Foundation Fundraising Bot
"""

import os
import sys
from email_generator import EmailGenerator

def test_email_generator():
    """Test the modular email generator"""
    print("🧪 Testing Modular Email Generator")
    print("=" * 50)
    
    # Initialize email generator
    generator = EmailGenerator()
    
    # Test 1: Get available templates
    print("\n📋 Test 1: Available Templates")
    templates = generator.get_available_templates()
    for template_type, description in templates.items():
        print(f"   • {template_type}: {description}")
    
    # Test 2: Get current mode
    print(f"\n🔧 Test 2: Current Mode")
    current_mode = generator.get_mode()
    print(f"   Current mode: {current_mode}")
    
    # Test 3: Set mode
    print(f"\n🔧 Test 3: Mode Management")
    result = generator.set_mode("template")
    print(f"   Set to template: {result}")
    
    result = generator.set_mode("claude")
    print(f"   Set to claude: {result}")
    
    # Test 4: Sample donor data
    print(f"\n🏢 Test 4: Sample Donor Data")
    sample_donor = {
        'organization_name': 'Test Foundation',
        'contact_person': 'John Doe',
        'sector_tags': 'Education Technology',
        'geography': 'Bihar',
        'alignment_score': '8',
        'priority': 'High',
        'current_stage': 'Engagement',
        'estimated_grant_size': '₹10,00,000',
        'notes': 'Interested in digital skills programs'
    }
    
    for key, value in sample_donor.items():
        print(f"   {key}: {value}")
    
    # Test 5: Generate template email
    print(f"\n📧 Test 5: Template Email Generation")
    subject, body = generator.generate_email('identification', sample_donor, 'template')
    print(f"   Subject: {subject}")
    print(f"   Body length: {len(body)} characters")
    print(f"   First 100 chars: {body[:100]}...")
    
    # Test 6: Generate Claude email (if API key available)
    print(f"\n🤖 Test 6: Claude Email Generation")
    claude_key = os.environ.get("ANTHROPIC_API_KEY")
    if claude_key:
        print(f"   Claude API key: ✅ Configured ({claude_key[:10]}...)")
        try:
            subject, body = generator.generate_email('identification', sample_donor, 'claude')
            print(f"   Subject: {subject}")
            print(f"   Body length: {len(body)} characters")
            print(f"   First 100 chars: {body[:100]}...")
        except Exception as e:
            print(f"   Claude generation failed: {e}")
    else:
        print("   Claude API key: ❌ Not configured")
        print("   Set ANTHROPIC_API_KEY environment variable to test Claude")
    
    # Test 7: Template comparison
    print(f"\n🔍 Test 7: Template Comparison")
    try:
        comparison = generator.compare_templates('identification', sample_donor)
        if comparison.get('ok'):
            metrics = comparison['comparison']['enhancement_metrics']
            print(f"   Similarity score: {metrics['similarity_score']}")
            print(f"   Improvement: {metrics['improvement_percentage']}%")
            print(f"   Length change: {metrics['length_change']} characters")
        else:
            print(f"   Comparison failed: {comparison.get('error')}")
    except Exception as e:
        print(f"   Comparison error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Modular Email Generator Test Complete!")
    
    if not claude_key:
        print("\n💡 To enable Claude AI enhancement:")
        print("   1. Get API key from [Anthropic Console](https://console.anthropic.com/)")
        print("   2. Set environment variable: export ANTHROPIC_API_KEY=your_key")
        print("   3. Run this test again")

if __name__ == "__main__":
    test_email_generator()

