#!/usr/bin/env python3
"""
Quick sample test to get a few real results from both crawlers.
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

print("Testing Enhanced Crawlers - Sample Results")
print("=" * 45)

print("Testing Asha Crawler (first 10 projects only)...")
try:
    from fundingbot_asha_crawler import crawler, settings

    # Test with expanded budget range and limited pages
    result = crawler.run(
        out_dir="./sample_out_asha",
        min_usd=1000,   # Much lower min
        max_usd=100000,  # Much higher max to catch more projects
        max_pages=1,     # Only 1 page (should get some projects)
        delay_sec=0.5,   # Faster for testing
        return_details=True
    )

    print(f"Asha Results: Found {len(result.rows)} proposals")
    if result.rows:
        print("Sample Asha Projects:")
        for i, row in enumerate(result.rows[:5]):  # Show first 5
            title = row.get('title', 'Unknown')
            budget = row.get('amount_requested_usd')
            location = row.get('geography', '')
            org = row.get('org', '')
            print(f"{i+1}. {title}")
            if budget:
                print(f"   Budget: ${budget:,.0f}")
            if location:
                print(f"   Location: {location}")
            if org:
                print(f"   Organization: {org}")
            print(f"   Link: {row.get('link', '')}")
            print()

except Exception as e:
    print(f"Asha test error: {e}")

print("\n" + "="*45)
print("Testing USAID Crawler (limited search)...")

try:
    from fundingbot_asha_crawler.usaid_crawler import run_usaid_crawler

    # Test with very limited scope
    usaid_result = run_usaid_crawler(
        out_dir="./sample_out_usaid",
        max_pages=3,    # Just a few sources
        delay_sec=1.0,
        return_details=True
    )

    print(f"USAID Results:")
    print(f"  Total documents found: {usaid_result.total_documents_found}")
    print(f"  Education-focused: {usaid_result.education_focused}")
    print(f"  Youth-focused: {usaid_result.youth_focused}")
    print(f"  Matching proposals: {len(usaid_result.rows)}")

    if usaid_result.rows:
        print("\nSample USAID Documents:")
        for i, row in enumerate(usaid_result.rows[:5]):
            title = row.get('title', 'Unknown')
            budget = row.get('amount_requested_usd')
            themes = row.get('themes', '')
            doc_type = row.get('document_type', '')
            print(f"{i+1}. {title}")
            if budget:
                print(f"   Budget: ${budget:,.0f}")
            print(f"   Themes: {themes}")
            print(f"   Type: {doc_type}")
            print(f"   Link: {row.get('link', '')}")
            print()

except Exception as e:
    print(f"USAID test error: {e}")
    import traceback
    traceback.print_exc()

print("\nSample test completed!")