"""
USAID Socrata API client for accessing machine-readable data.
"""

import requests
import json
from typing import List, Dict, Any, Optional
from urllib.parse import urlencode
import logging

log = logging.info

class USAIDAPIClient:
    """Client for accessing USAID data via Socrata Open Data API."""

    def __init__(self):
        self.base_url = "https://data.usaid.gov/resource"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; FundingBot/usaid-api; +https://example.org)",
            "Accept": "application/json"
        }

    def search_datasets(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for datasets by keyword."""
        try:
            # Search the catalog for education/youth related datasets
            search_url = "https://data.usaid.gov/api/catalog/v1"
            params = {
                "q": query,
                "limit": limit,
                "only": "datasets"
            }

            response = requests.get(search_url, headers=self.headers, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])
            else:
                log(f"Dataset search failed: {response.status_code}")
                return []

        except Exception as e:
            log(f"Error searching datasets: {e}")
            return []

    def get_dataset_data(self, dataset_id: str, filters: Optional[Dict] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get data from a specific dataset using Socrata SODA API."""
        try:
            url = f"{self.base_url}/{dataset_id}.json"
            params = {"$limit": limit}

            # Add filters if provided
            if filters:
                for key, value in filters.items():
                    params[key] = value

            response = requests.get(url, headers=self.headers, params=params, timeout=20)
            if response.status_code == 200:
                return response.json()
            else:
                log(f"Dataset {dataset_id} request failed: {response.status_code}")
                return []

        except Exception as e:
            log(f"Error fetching dataset {dataset_id}: {e}")
            return []

    def search_education_youth_projects(self) -> List[Dict[str, Any]]:
        """Search for education and youth-related projects."""
        education_terms = ["education", "youth", "school", "training", "learning", "children"]
        all_results = []

        for term in education_terms:
            log(f"Searching for '{term}' related datasets...")
            results = self.search_datasets(term, limit=20)

            for dataset in results:
                # Check if dataset is education/youth related
                title = dataset.get("resource", {}).get("name", "").lower()
                description = dataset.get("resource", {}).get("description", "").lower()

                if any(edu_term in title or edu_term in description for edu_term in education_terms):
                    all_results.append(dataset)

        # Remove duplicates based on dataset ID
        seen_ids = set()
        unique_results = []
        for result in all_results:
            dataset_id = result.get("resource", {}).get("id")
            if dataset_id and dataset_id not in seen_ids:
                seen_ids.add(dataset_id)
                unique_results.append(result)

        return unique_results

    def extract_project_details(self, dataset_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract project details from dataset metadata."""
        try:
            resource = dataset_info.get("resource", {})

            # Try to get the actual data if it's a small dataset
            dataset_id = resource.get("id")
            if not dataset_id:
                return None

            # Get dataset data
            data_rows = self.get_dataset_data(dataset_id, limit=10)

            # Extract key information
            project_data = {
                "title": resource.get("name", "Unknown"),
                "description": resource.get("description", ""),
                "dataset_id": dataset_id,
                "url": f"https://data.usaid.gov/d/{dataset_id}",
                "organization": "USAID",
                "created_date": resource.get("createdAt", ""),
                "updated_date": resource.get("updatedAt", ""),
                "row_count": resource.get("rowsUpdatedAt", 0),
                "data_sample": data_rows[:3] if data_rows else []  # First 3 rows as sample
            }

            # Try to extract budget/amount information from data
            budget_amount = None
            if data_rows:
                for row in data_rows:
                    for key, value in row.items():
                        if any(budget_term in key.lower() for budget_term in ["amount", "budget", "funding", "cost"]):
                            try:
                                # Try to extract numeric value
                                if isinstance(value, (int, float)):
                                    budget_amount = float(value)
                                    break
                                elif isinstance(value, str):
                                    import re
                                    amount_match = re.search(r'[\d,]+\.?\d*', value.replace(",", ""))
                                    if amount_match:
                                        budget_amount = float(amount_match.group().replace(",", ""))
                                        break
                            except:
                                continue
                    if budget_amount:
                        break

            project_data["estimated_budget_usd"] = budget_amount

            return project_data

        except Exception as e:
            log(f"Error extracting project details: {e}")
            return None

def test_usaid_api():
    """Test function for USAID API client."""
    print("Testing USAID Socrata API Client")
    print("=" * 40)

    client = USAIDAPIClient()

    # Search for education/youth datasets
    datasets = client.search_education_youth_projects()
    print(f"Found {len(datasets)} education/youth related datasets")

    if datasets:
        print("\nSample datasets:")
        for i, dataset in enumerate(datasets[:5]):
            resource = dataset.get("resource", {})
            print(f"{i+1}. {resource.get('name', 'Unknown')}")
            print(f"   ID: {resource.get('id', 'N/A')}")
            print(f"   Description: {resource.get('description', 'N/A')[:100]}...")
            print()

        # Get detailed info for first dataset
        if datasets:
            print("Getting detailed info for first dataset...")
            details = client.extract_project_details(datasets[0])
            if details:
                print("Dataset Details:")
                for key, value in details.items():
                    if key != "data_sample":
                        print(f"  {key}: {value}")

    return datasets

if __name__ == "__main__":
    test_usaid_api()