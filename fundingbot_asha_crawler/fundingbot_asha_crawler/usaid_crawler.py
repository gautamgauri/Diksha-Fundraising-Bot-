"""
USAID crawler utilities for harvesting education/youth proposals under $100K.
"""

import os
import re
import time
import csv
import logging
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

from . import usaid_settings
from .crawler import (
    safe_filename, ext_of, get, download_file, parse_pdf_text,
    normalize_number, _get_drive_service, upload_csv_to_drive
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.info

USAID_HEADERS = {"User-Agent": usaid_settings.USAID_USER_AGENT}

@dataclass
class USAIDProposalRecord:
    title: str
    organization: str
    year: Optional[int]
    funding_agency: str
    currency: str
    amount_requested_usd: Optional[float]
    link: str
    file_path: str
    themes: str  # education, youth, or both
    geography: str
    duration_months: Optional[int]
    document_type: str
    education_score: int
    youth_score: int
    notes: str

@dataclass
class USAIDRunResult:
    csv_path: str
    rows: List[Dict[str, Any]]
    total_documents_found: int
    education_focused: int
    youth_focused: int
    under_budget_threshold: int
    uploaded_to_drive: bool = False
    drive_file_id: Optional[str] = None
    drive_web_link: Optional[str] = None
    drive_folder_id: Optional[str] = None

# Enhanced regex patterns for USAID documents
USD_BUDGET_PAT = re.compile(r"(\$|USD|US\$|dollars?)\s*([0-9][0-9,\. ]+)", re.I)
TOTAL_BUDGET_HINTS = re.compile(r"(total\s*budget|project\s*cost|funding\s*amount|award\s*amount|grant\s*amount|budget\s*total)", re.I)
YEAR_PAT = re.compile(r"\b(20[0-4][0-9])\b")

# Document type detection patterns
DOC_TYPE_PATTERNS = {
    "proposal": re.compile(r"(proposal|application|submission)", re.I),
    "evaluation": re.compile(r"(evaluation|assessment|review)", re.I),
    "report": re.compile(r"(report|study|analysis)", re.I),
    "grant": re.compile(r"(grant|award|funding)", re.I),
    "technical": re.compile(r"(technical|guidance|manual)", re.I)
}

def is_usaid_allowed(url: str) -> bool:
    """Check if URL is from allowed USAID domains."""
    host = urlparse(url).netloc.lower().replace("www.", "")
    return any(host.endswith(domain) for domain in usaid_settings.USAID_ALLOWED_DOMAINS)

def looks_like_usaid_doc(url: str) -> bool:
    """Check if URL looks like a USAID document."""
    ext = ext_of(url)
    if ext in usaid_settings.USAID_DOC_EXTS:
        return True

    url_lower = url.lower()
    return any(doc_type in url_lower for doc_type in usaid_settings.USAID_PRIORITY_DOC_TYPES)

def extract_usd_budget(text: str) -> Tuple[Optional[float], str]:
    """Extract USD budget amount from proposal text."""
    if not text:
        return None, "no_text"

    # Look for budget hints in the text
    for line in text.splitlines():
        if TOTAL_BUDGET_HINTS.search(line):
            for match in USD_BUDGET_PAT.finditer(line):
                amount_str = match.group(2)
                amount = normalize_number(amount_str)
                if amount:
                    amount_float = float(amount)
                    if usaid_settings.MIN_USD_BUDGET <= amount_float <= usaid_settings.MAX_USD_BUDGET:
                        return amount_float, f"found_in_budget_hint: {line.strip()[:100]}"

    # If no budget hint found, look for any USD amounts
    for match in USD_BUDGET_PAT.finditer(text):
        amount_str = match.group(2)
        amount = normalize_number(amount_str)
        if amount:
            amount_float = float(amount)
            if usaid_settings.MIN_USD_BUDGET <= amount_float <= usaid_settings.MAX_USD_BUDGET:
                return amount_float, "found_general_amount"

    return None, "no_amount_found"

def analyze_education_youth_themes(text: str) -> Tuple[bool, str, int, int]:
    """Analyze if document focuses on education/youth themes."""
    if not text:
        return False, "", 0, 0

    text_lower = text.lower()

    # Count keyword occurrences
    education_score = sum(1 for keyword in usaid_settings.EDUCATION_KEYWORDS if keyword in text_lower)
    youth_score = sum(1 for keyword in usaid_settings.YOUTH_KEYWORDS if keyword in text_lower)

    # Determine if document is relevant
    is_relevant = education_score >= 3 or youth_score >= 2

    themes = []
    if education_score >= 3:
        themes.append("education")
    if youth_score >= 2:
        themes.append("youth")

    theme_string = ", ".join(themes) if themes else ""

    return is_relevant, theme_string, education_score, youth_score

def detect_document_type(text: str, url: str) -> str:
    """Detect the type of document based on content and URL."""
    text_lower = text.lower() if text else ""
    url_lower = url.lower()

    # Check URL first
    for doc_type, pattern in DOC_TYPE_PATTERNS.items():
        if pattern.search(url_lower):
            return doc_type

    # Check content
    for doc_type, pattern in DOC_TYPE_PATTERNS.items():
        if pattern.search(text_lower):
            return doc_type

    return "unknown"

def get_usaid_document(url: str, timeout: int = 30):
    """Get USAID document with appropriate headers."""
    try:
        response = requests.get(url, headers=USAID_HEADERS, timeout=timeout)
        if response.status_code == 200:
            return response
        return None
    except requests.RequestException as e:
        log(f"Error fetching {url}: {e}")
        return None

def extract_decfinder_results(search_url: str) -> List[Dict[str, Any]]:
    """Extract document results from DECfinder search pages."""
    try:
        response = get_usaid_document(search_url)
        if not response:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        # Look for document entries in the search results
        # DECfinder typically shows documents in cards or list items
        for card in soup.find_all(["div", "article", "li"], class_=re.compile(r"(result|document|card|item)", re.I)):
            doc_data = {}

            # Extract title
            title_elem = card.find(["h1", "h2", "h3", "h4", "a"], string=re.compile(r".+"))
            if title_elem:
                doc_data["title"] = title_elem.get_text(strip=True)

            # Extract link
            link_elem = card.find("a", href=True)
            if link_elem:
                doc_data["link"] = urljoin(search_url, link_elem["href"])

            # Extract description/summary
            desc_elem = card.find(["p", "div"], string=re.compile(r".{20,}"))
            if desc_elem:
                doc_data["description"] = desc_elem.get_text(strip=True)[:500]

            # Look for metadata (year, location, etc.)
            for meta in card.find_all(["span", "small", "div"], class_=re.compile(r"(meta|date|year|location)", re.I)):
                text = meta.get_text(strip=True)
                year_match = re.search(r"20[0-2][0-9]", text)
                if year_match:
                    doc_data["year"] = int(year_match.group())

            if doc_data.get("title") and doc_data.get("link"):
                results.append(doc_data)

        return results

    except Exception as e:
        log(f"Error extracting DECfinder results from {search_url}: {e}")
        return []

def extract_data_gov_results(catalog_url: str) -> List[Dict[str, Any]]:
    """Extract dataset results from Data.gov catalog."""
    try:
        response = get_usaid_document(catalog_url)
        if not response:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        # Look for dataset entries
        for dataset in soup.find_all(["div", "article"], class_=re.compile(r"(dataset|resource)", re.I)):
            doc_data = {}

            # Extract title
            title_elem = dataset.find(["h3", "h4", "a"])
            if title_elem:
                doc_data["title"] = title_elem.get_text(strip=True)

            # Extract link
            link_elem = dataset.find("a", href=True)
            if link_elem:
                doc_data["link"] = urljoin(catalog_url, link_elem["href"])

            # Extract description
            desc_elem = dataset.find(["p", "div"], class_=re.compile(r"(description|notes)", re.I))
            if desc_elem:
                doc_data["description"] = desc_elem.get_text(strip=True)[:500]

            if doc_data.get("title") and doc_data.get("link"):
                results.append(doc_data)

        return results

    except Exception as e:
        log(f"Error extracting Data.gov results from {catalog_url}: {e}")
        return []

def crawl_usaid_documents(seed_urls: List[str], max_pages: int, delay_sec: float) -> List[Dict[str, Any]]:
    """Crawl USAID sites for relevant documents with enhanced extraction."""
    all_documents = []

    # Use specific search URLs for better targeting
    search_urls = usaid_settings.USAID_SEARCH_URLS + seed_urls

    for i, url in enumerate(search_urls[:max_pages]):
        log(f"Processing USAID source {i+1}/{min(len(search_urls), max_pages)}: {url}")
        time.sleep(delay_sec)

        try:
            if "decfinder.devme.ai" in url:
                documents = extract_decfinder_results(url)
                all_documents.extend(documents)
            elif "catalog.data.gov" in url:
                documents = extract_data_gov_results(url)
                all_documents.extend(documents)
            elif "data.usaid.gov" in url:
                # For data.usaid.gov, we'll use a simpler link extraction
                response = get_usaid_document(url)
                if response:
                    soup = BeautifulSoup(response.text, "html.parser")
                    for link in soup.find_all("a", href=True):
                        href = link["href"]
                        if any(ext in href for ext in [".pdf", ".doc", ".csv"]):
                            all_documents.append({
                                "title": link.get_text(strip=True) or "USAID Dataset",
                                "link": urljoin(url, href),
                                "description": "Dataset from USAID Development Data Library"
                            })

        except Exception as e:
            log(f"Error processing USAID source {url}: {e}")

    # Remove duplicates based on link
    seen_links = set()
    unique_documents = []
    for doc in all_documents:
        if doc.get("link") not in seen_links:
            seen_links.add(doc["link"])
            unique_documents.append(doc)

    log(f"Found {len(unique_documents)} unique USAID documents from {len(search_urls)} sources")
    return unique_documents

def run_usaid_crawler(
    out_dir: str = "./usaid_out",
    max_pages: int = usaid_settings.DEFAULT_USAID_MAX_PAGES,
    delay_sec: float = usaid_settings.DEFAULT_USAID_DELAY_SEC,
    seeds: Optional[List[str]] = None,
    upload_to_drive: bool = False,
    drive_folder_id: Optional[str] = None,
    return_details: bool = False,
) -> USAIDRunResult | str:
    """Run USAID-specific crawler for education/youth proposals under $100K."""
    try:
        seed_urls = seeds or usaid_settings.USAID_SEEDS
        download_dir = os.path.join(out_dir, "usaid_downloads")
        os.makedirs(download_dir, exist_ok=True)

        log("Starting USAID crawl for education/youth proposals...")
        document_data = crawl_usaid_documents(seed_urls, max_pages, delay_sec)
        log(f"USAID crawl finished. Found {len(document_data)} documents.")

        rows: List[Dict[str, Any]] = []
        stats = {
            "education_focused": 0,
            "youth_focused": 0,
            "under_budget_threshold": 0
        }

        for i, doc_info in enumerate(document_data):
            log(f"Processing USAID document {i+1}/{len(document_data)}: {doc_info.get('title', 'Unknown')}")

            # Use existing description/title for analysis instead of downloading
            title = doc_info.get("title", "")
            description = doc_info.get("description", "")
            combined_text = f"{title} {description}"
            link = doc_info.get("link", "")

            # Try to download document if it's a PDF for detailed analysis
            file_path = ""
            detailed_text = ""
            if link.endswith(".pdf"):
                file_path = download_file(link, download_dir)
                if file_path:
                    detailed_text = parse_pdf_text(file_path)
                    combined_text += f" {detailed_text}"

            # Analyze budget from combined text
            amount_usd, budget_note = extract_usd_budget(combined_text)

            # Get year from document info or text
            year = doc_info.get("year")
            if not year and combined_text:
                year_matches = YEAR_PAT.findall(combined_text)
                year = int(max(year_matches)) if year_matches else None

            # Analyze education/youth themes
            is_relevant, themes, edu_score, youth_score = analyze_education_youth_themes(combined_text)

            # Only include if relevant to education/youth AND within budget
            if is_relevant and (amount_usd is None or amount_usd <= usaid_settings.MAX_USD_BUDGET):
                doc_type = detect_document_type(combined_text, link)

                record = USAIDProposalRecord(
                    title=title or "USAID Document",
                    organization="",  # Could be extracted from text if needed
                    year=year,
                    funding_agency="USAID",
                    currency="USD" if amount_usd else "",
                    amount_requested_usd=amount_usd,
                    link=link,
                    file_path=file_path,
                    themes=themes,
                    geography="",  # Could be extracted from text if needed
                    duration_months=None,  # Could be extracted from text if needed
                    document_type=doc_type,
                    education_score=edu_score,
                    youth_score=youth_score,
                    notes=f"{budget_note}; {description[:200]}..." if description else budget_note,
                )

                rows.append(asdict(record))

                # Update statistics
                if "education" in themes:
                    stats["education_focused"] += 1
                if "youth" in themes:
                    stats["youth_focused"] += 1
                if amount_usd and amount_usd <= usaid_settings.MAX_USD_BUDGET:
                    stats["under_budget_threshold"] += 1

        log(f"Finished processing USAID documents. Found {len(rows)} matching proposals.")
        log(f"Statistics: {stats['education_focused']} education-focused, {stats['youth_focused']} youth-focused, {stats['under_budget_threshold']} under budget threshold")

        # Save results
        csv_path = os.path.join(out_dir, "usaid_proposals.csv")
        log(f"Saving USAID results to {csv_path}")

        fieldnames = list(rows[0].keys()) if rows else [
            "title", "amount_requested_usd", "themes", "link", "document_type", "notes"
        ]

        with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            if rows:
                writer.writerows(rows)

        # Optional Google Drive upload
        drive_info: Optional[Dict[str, Any]] = None
        target_folder = drive_folder_id or os.environ.get("FUNDINGBOT_DRIVE_FOLDER_ID")
        if upload_to_drive and target_folder:
            drive_info = upload_csv_to_drive(csv_path, target_folder)

        result = USAIDRunResult(
            csv_path=csv_path,
            rows=rows,
            total_documents_found=len(document_links),
            education_focused=stats["education_focused"],
            youth_focused=stats["youth_focused"],
            under_budget_threshold=stats["under_budget_threshold"],
            uploaded_to_drive=bool(drive_info),
            drive_file_id=(drive_info or {}).get("id"),
            drive_web_link=(drive_info or {}).get("webViewLink"),
            drive_folder_id=target_folder,
        )

        return result if return_details else result.csv_path

    except Exception as e:
        logging.error(f"Error during USAID crawler run: {e}")
        return USAIDRunResult(
            csv_path="", rows=[], total_documents_found=0,
            education_focused=0, youth_focused=0, under_budget_threshold=0
        ) if return_details else ""