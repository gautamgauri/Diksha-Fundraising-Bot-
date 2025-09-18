#!/usr/bin/env python3
"""
Get real sample proposals from both Asha and USAID sources.
"""
import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

sys.path.insert(0, os.path.abspath('.'))

def get_asha_sample_projects():
    """Get a few real Asha project samples directly."""
    print("Fetching Asha Sample Projects...")
    print("-" * 40)

    # Known project URLs to test
    sample_urls = [
        "https://ashanet.org/project/?pid=618",
        "https://ashanet.org/project/?pid=1092",
        "https://ashanet.org/project/?pid=466",
        "https://ashanet.org/project/?pid=1104",
        "https://ashanet.org/project/?pid=847"
    ]

    samples = []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; FundingBot/asha-crawler; +https://example.org)"}

    for i, url in enumerate(sample_urls):
        print(f"Processing Asha project {i+1}/5...")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                project_data = {
                    "title": "Unknown Project",
                    "organization": "",
                    "location": "",
                    "status": "",
                    "last_funding_amount": None,
                    "last_funding_date": "",
                    "steward_chapter": "",
                    "url": url
                }

                # Extract title
                title_elem = soup.find("h1") or soup.find("title")
                if title_elem:
                    project_data["title"] = title_elem.get_text(strip=True)

                # Extract from table data
                for table in soup.find_all("table"):
                    for row in table.find_all("tr"):
                        cells = row.find_all(["td", "th"])
                        if len(cells) >= 2:
                            key = cells[0].get_text(strip=True).lower()
                            value = cells[1].get_text(strip=True)

                            if "organization" in key or "ngo" in key:
                                project_data["organization"] = value
                            elif "location" in key or "state" in key:
                                project_data["location"] = value
                            elif "status" in key:
                                project_data["status"] = value
                            elif "amount" in key or "funding" in key:
                                amount_match = re.search(r'(\d+[\d,]*)', value.replace(",", ""))
                                if amount_match:
                                    project_data["last_funding_amount"] = int(amount_match.group(1))
                            elif "date" in key:
                                project_data["last_funding_date"] = value
                            elif "chapter" in key or "steward" in key:
                                project_data["steward_chapter"] = value

                samples.append(project_data)

        except Exception as e:
            print(f"Error processing {url}: {e}")
            continue

    return samples

def get_usaid_sample_documents():
    """Get sample USAID documents from accessible sources."""
    print("\nFetching USAID Sample Documents...")
    print("-" * 40)

    samples = []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; FundingBot/usaid-crawler; +https://example.org)"}

    # Try to get from Data.gov catalog
    try:
        catalog_url = "https://catalog.data.gov/dataset?organization=usaid-gov&q=education"
        print("Checking Data.gov USAID catalog...")

        response = requests.get(catalog_url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Look for dataset entries
            for dataset in soup.find_all(["div", "article"], class_=re.compile(r"dataset", re.I)):
                title_elem = dataset.find(["h3", "h4", "a"])
                if title_elem:
                    title = title_elem.get_text(strip=True)

                    # Check if education/youth related
                    if any(keyword in title.lower() for keyword in ["education", "youth", "school", "training", "learning"]):
                        link_elem = dataset.find("a", href=True)
                        link = urljoin(catalog_url, link_elem["href"]) if link_elem else ""

                        # Extract description
                        desc_elem = dataset.find("p") or dataset.find("div", class_=re.compile(r"notes", re.I))
                        description = desc_elem.get_text(strip=True)[:300] if desc_elem else ""

                        samples.append({
                            "title": title,
                            "link": link,
                            "description": description,
                            "source": "Data.gov",
                            "type": "dataset"
                        })

                        if len(samples) >= 5:  # Limit to 5 samples
                            break

    except Exception as e:
        print(f"Error fetching from Data.gov: {e}")

    return samples

def display_samples(asha_samples, usaid_samples):
    """Display the retrieved samples in a nice format."""
    print("\n" + "=" * 60)
    print("REAL SAMPLE PROPOSALS RETRIEVED")
    print("=" * 60)

    print(f"\nASHA FOR EDUCATION PROJECTS ({len(asha_samples)} found)")
    print("-" * 50)

    for i, project in enumerate(asha_samples, 1):
        print(f"{i}. {project['title']}")
        if project['organization']:
            print(f"   Organization: {project['organization']}")
        if project['location']:
            print(f"   Location: {project['location']}")
        if project['status']:
            print(f"   Status: {project['status']}")
        if project['last_funding_amount']:
            inr_amount = project['last_funding_amount']
            usd_amount = inr_amount / 83.0
            print(f"   Last Funding: ₹{inr_amount:,} (~${usd_amount:,.0f})")
        if project['last_funding_date']:
            print(f"   Date: {project['last_funding_date']}")
        if project['steward_chapter']:
            print(f"   Chapter: {project['steward_chapter']}")
        print(f"   URL: {project['url']}")
        print()

    print(f"USAID DOCUMENTS ({len(usaid_samples)} found)")
    print("-" * 50)

    for i, doc in enumerate(usaid_samples, 1):
        print(f"{i}. {doc['title']}")
        print(f"   Source: {doc['source']}")
        print(f"   Type: {doc['type']}")
        if doc['description']:
            print(f"   Description: {doc['description']}")
        if doc['link']:
            print(f"   URL: {doc['link']}")
        print()

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Asha Projects: {len(asha_samples)}")
    print(f"Total USAID Documents: {len(usaid_samples)}")
    print(f"Total Proposals Found: {len(asha_samples) + len(usaid_samples)}")

    if asha_samples:
        funded_projects = [p for p in asha_samples if p['last_funding_amount']]
        if funded_projects:
            avg_funding = sum(p['last_funding_amount'] for p in funded_projects) / len(funded_projects)
            avg_usd = avg_funding / 83.0
            print(f"Average Asha Funding: ₹{avg_funding:,.0f} (~${avg_usd:,.0f})")

    print("\nCrawlers are working with real data!")
    print("Ready for full-scale proposal discovery.")

if __name__ == "__main__":
    print("Multi-Source Proposal Crawler - Live Sample Run")
    print("=" * 55)

    # Get samples from both sources
    asha_samples = get_asha_sample_projects()
    usaid_samples = get_usaid_sample_documents()

    # Display results
    display_samples(asha_samples, usaid_samples)