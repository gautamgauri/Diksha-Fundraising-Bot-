#!/usr/bin/env python3
"""
Demonstration of crawler results with sample realistic proposals.
"""
import pandas as pd
import os

def demonstrate_crawler_results():
    """Show what the crawler results would look like with real data."""

    print("Multi-Source Funding Proposal Discovery - Demo Results")
    print("=" * 60)

    # Load sample data
    sample_file = "sample_proposals_demo.csv"
    if not os.path.exists(sample_file):
        print(f"Error: {sample_file} not found")
        return

    df = pd.read_csv(sample_file)

    # Overall statistics
    total_proposals = len(df)
    asha_proposals = len(df[df['source'] == 'asha'])
    usaid_proposals = len(df[df['source'] == 'usaid'])

    avg_budget_asha = df[df['source'] == 'asha']['amount_requested_usd'].mean()
    avg_budget_usaid = df[df['source'] == 'usaid']['amount_requested_usd'].mean()

    print(f"SUMMARY STATISTICS:")
    print(f"Total Proposals Found: {total_proposals}")
    print(f"- Asha for Education: {asha_proposals} proposals")
    print(f"- USAID Archives: {usaid_proposals} proposals")
    print(f"")
    print(f"BUDGET ANALYSIS:")
    print(f"- Asha Average Budget: ${avg_budget_asha:,.0f}")
    print(f"- USAID Average Budget: ${avg_budget_usaid:,.0f}")
    print(f"- Total Portfolio Value: ${df['amount_requested_usd'].sum():,.0f}")

    print(f"\n" + "=" * 60)
    print("ASHA FOR EDUCATION PROPOSALS (India-focused)")
    print("=" * 60)

    asha_df = df[df['source'] == 'asha']
    for i, row in asha_df.iterrows():
        print(f"{i+1}. {row['title']}")
        print(f"   Organization: {row['org']}")
        print(f"   Budget: ${row['amount_requested_usd']:,} (~INR {row['amount_inr']:,})")
        print(f"   Location: {row['geography']}")
        print(f"   Focus: {row['focus_area']}")
        print(f"   Duration: {row['duration_months']} months")
        print(f"   Funder: {row['chapter_or_funder']}")
        print(f"   Year: {row['year']}")
        print(f"   Link: {row['link']}")
        print()

    print("=" * 60)
    print("USAID PROPOSALS (Global education/youth)")
    print("=" * 60)

    usaid_df = df[df['source'] == 'usaid']
    for i, row in usaid_df.iterrows():
        print(f"{i+1}. {row['title']}")
        print(f"   Organization: {row['org']}")
        print(f"   Budget: ${row['amount_requested_usd']:,}")
        print(f"   Location: {row['geography']}")
        print(f"   Focus: {row['focus_area']}")
        print(f"   Duration: {row['duration_months']} months")
        print(f"   Year: {row['year']}")
        print(f"   Link: {row['link']}")
        print()

    print("=" * 60)
    print("ANALYSIS INSIGHTS")
    print("=" * 60)

    # Focus area analysis
    focus_areas = df['focus_area'].value_counts()
    print("Focus Areas Distribution:")
    for area, count in focus_areas.items():
        print(f"- {area}: {count} proposals")

    print(f"\nGeographic Distribution:")
    locations = df['geography'].value_counts()
    for location, count in locations.items():
        print(f"- {location}: {count} proposals")

    print(f"\nBudget Range Analysis:")
    budget_ranges = {
        "Under $40K": len(df[df['amount_requested_usd'] < 40000]),
        "$40K - $60K": len(df[(df['amount_requested_usd'] >= 40000) & (df['amount_requested_usd'] < 60000)]),
        "$60K - $80K": len(df[(df['amount_requested_usd'] >= 60000) & (df['amount_requested_usd'] < 80000)]),
        "$80K+": len(df[df['amount_requested_usd'] >= 80000])
    }

    for range_name, count in budget_ranges.items():
        print(f"- {range_name}: {count} proposals")

    print(f"\n" + "=" * 60)
    print("CRAWLER IMPLEMENTATION STATUS")
    print("=" * 60)

    print("✅ IMPLEMENTED FEATURES:")
    print("- Multi-source crawler architecture")
    print("- USD-based budget filtering for both sources")
    print("- Education/youth keyword detection")
    print("- Streamlit web interface")
    print("- CSV export with detailed metadata")
    print("- Google Drive integration")
    print("- Document type classification")
    print("- Geographic and thematic analysis")

    print(f"\n⚠️  CURRENT LIMITATIONS:")
    print("- Asha site requires deeper crawling to individual project pages")
    print("- USAID DEC requires specific search queries or authentication")
    print("- Some document repositories may have access restrictions")
    print("- Real-time crawling depends on site structure and rate limits")

    print(f"\n🔧 NEXT STEPS FOR PRODUCTION:")
    print("- Configure specific search queries for USAID repositories")
    print("- Implement individual Asha project page crawling")
    print("- Add authentication for restricted document repositories")
    print("- Set up scheduled crawling for regular updates")
    print("- Integrate with your existing pipeline management system")

if __name__ == "__main__":
    demonstrate_crawler_results()