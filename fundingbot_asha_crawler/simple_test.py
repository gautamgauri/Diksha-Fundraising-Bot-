#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test for both crawlers.
"""
import sys
import os

# Set UTF-8 encoding for Windows
import locale
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

sys.path.insert(0, os.path.abspath('.'))

# Test Asha crawler first (simpler)
print("Testing Asha Crawler (USD mode)")
print("=" * 40)

try:
    from fundingbot_asha_crawler import crawler, settings

    # Test with very limited scope
    result = crawler.run(
        out_dir="./test_out_asha",
        min_usd=30000,  # $30K
        max_usd=50000,  # $50K
        max_pages=2,    # Very limited for testing
        delay_sec=1.0,
        return_details=True
    )

    print(f"✅ Asha crawler test completed!")
    if hasattr(result, 'rows'):
        print(f"📄 Found {len(result.rows)} proposals")
        if result.rows:
            print("\n📋 Sample Asha proposals:")
            for i, row in enumerate(result.rows[:3]):
                print(f"{i+1}. {row['title']}")
                print(f"   Budget: ${row['amount_requested_usd']:,}" if row['amount_requested_usd'] else "   Budget: Not specified")
                print(f"   Link: {row['link']}")
                print()
    else:
        print("⚠️ No results returned")

except Exception as e:
    print(f"❌ Asha crawler error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("🎯 Testing USAID Crawler (Education/Youth)")
print("=" * 50)

# For USAID, let's try a simpler approach - just check if the modules load
try:
    from fundingbot_asha_crawler.usaid_crawler import run_usaid_crawler
    print("✅ USAID crawler module loaded successfully")

    # Try a very minimal test
    print("🔍 Running minimal USAID test...")
    usaid_result = run_usaid_crawler(
        out_dir="./test_out_usaid",
        max_pages=1,  # Just 1 page for testing
        delay_sec=2.0,
        return_details=True
    )

    print(f"✅ USAID crawler test completed!")
    if hasattr(usaid_result, 'rows'):
        print(f"📄 Total documents found: {usaid_result.total_documents_found}")
        print(f"🎓 Education-focused: {usaid_result.education_focused}")
        print(f"👥 Youth-focused: {usaid_result.youth_focused}")
        print(f"💰 Under budget: {usaid_result.under_budget_threshold}")
        print(f"📝 Matching proposals: {len(usaid_result.rows)}")

        if usaid_result.rows:
            print("\n📋 Sample USAID proposals:")
            for i, row in enumerate(usaid_result.rows[:3]):
                print(f"{i+1}. {row['title']}")
                print(f"   Budget: ${row['amount_requested_usd']:,}" if row['amount_requested_usd'] else "   Budget: Not specified")
                print(f"   Themes: {row['themes']}")
                print(f"   Type: {row['document_type']}")
                print()
    else:
        print("⚠️ No USAID results returned")

except Exception as e:
    print(f"❌ USAID crawler error: {e}")
    import traceback
    traceback.print_exc()

print("\n🏁 Test completed!")