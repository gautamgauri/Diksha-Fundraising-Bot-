"""
Asha crawler utilities for harvesting proposals from ashanet.org.
"""

import os
import re
import time
import csv
import logging
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

from . import settings

# Optional Google Drive integration
try:
    from backend.core.google_auth import create_google_clients  # type: ignore
    from googleapiclient.http import MediaFileUpload  # type: ignore
    from googleapiclient.errors import HttpError  # type: ignore
    _DRIVE_SUPPORTED = True
except Exception:  # pragma: no cover - optional dependency
    create_google_clients = None  # type: ignore
    MediaFileUpload = None  # type: ignore
    HttpError = Exception  # type: ignore
    _DRIVE_SUPPORTED = False

HEADERS = {"User-Agent": settings.USER_AGENT}


@dataclass
class ProposalRecord:
    title: str
    org: str
    year: Optional[int]
    chapter_or_funder: str
    currency: str
    amount_requested_usd: Optional[float]  # Changed to USD for consistency
    amount_inr: Optional[int]  # Keep INR for reference
    link: str
    file_path: str
    focus_area: str
    geography: str
    duration_months: Optional[int]
    notes: str


@dataclass
class RunResult:
    csv_path: str
    rows: List[Dict[str, Any]]
    uploaded_to_drive: bool = False
    drive_file_id: Optional[str] = None
    drive_web_link: Optional[str] = None
    drive_folder_id: Optional[str] = None


_DRIVE_SERVICE = None
_DRIVE_INIT_ATTEMPTED = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.info



def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "_", value.strip())
    return cleaned[:200]


def ext_of(url: str) -> str:
    path = urlparse(url).path
    _, _, ext = path.rpartition(".")
    return f".{ext.lower()}" if ext else ""


def get(url: str, timeout: int = 20):
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        if response.status_code == 200:
            return response
        return None
    except requests.RequestException:
        return None


def is_allowed(url: str) -> bool:
    host = urlparse(url).netloc.lower().replace("www.", "")
    return any(host.endswith(domain) for domain in settings.ALLOWED_DOMAINS)


def looks_like_doc(url: str) -> bool:
    ext = ext_of(url)
    if ext in settings.DOC_EXTS:
        return True
    return "proposal" in url.lower()


def absolute_links(base_url: str, html: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    return [urljoin(base_url, anchor["href"]) for anchor in soup.find_all("a", href=True)]


BUDGET_HINTS = re.compile(r"(asha\s*request|total\s*requested|amount\s*requested|budget)", re.I)
INR_PAT = re.compile(r"(?:\u20b9|rs\\.?|inr)\\s*([0-9][0-9,\\. ]+)", re.I)
USD_PAT = re.compile(r"(\$)\s*([0-9][0-9,\. ]+)", re.I)
YEAR_PAT = re.compile(r"\b(20[0-4][0-9])\b")


def parse_pdf_text(pdf_path: str) -> str:
    if fitz is None:
        return ""
    try:
        pages: List[str] = []
        with fitz.open(pdf_path) as doc:  # type: ignore[attr-defined]
            for page in doc:
                pages.append(page.get_text())
        return "\n".join(pages)
    except Exception:
        return ""


def normalize_number(num_str: str) -> Optional[int]:
    try:
        cleaned = num_str.replace(",", "").replace(" ", "")
        return int(round(float(cleaned)))
    except Exception:
        return None


def pick_amount_from_text(text: str, usd_rate: float):
    if not text:
        return None, None, "no_text"
    for line in text.splitlines():
        if BUDGET_HINTS.search(line):
            for match in INR_PAT.finditer(line):
                amount = normalize_number(match.group(2))
                if amount:
                    return amount, round(amount / usd_rate, 2), "inr_hint"
            for match in USD_PAT.finditer(line):
                amount = normalize_number(match.group(2))
                if amount:
                    return int(round(amount * usd_rate)), float(amount), "usd_hint"
    return None, None, "no_amount_found"


def guess_year(text: str) -> Optional[int]:
    years = YEAR_PAT.findall(text)
    if not years:
        return None
    return max(map(int, years))


def download_file(url: str, out_dir: str) -> Optional[str]:
    os.makedirs(out_dir, exist_ok=True)
    filename = safe_filename(os.path.basename(urlparse(url).path) or "download.pdf")
    dest_path = os.path.join(out_dir, filename)
    try:
        with requests.get(url, headers=HEADERS, stream=True, timeout=30) as response:
            if response.status_code != 200:
                return None
            with open(dest_path, "wb") as output:
                for chunk in response.iter_content(8192):
                    if chunk:
                        output.write(chunk)
        return dest_path
    except requests.RequestException:
        return None


def within_band(value: Optional[float], min_usd: float, max_usd: float) -> bool:
    """Check if USD amount is within specified band."""
    return value is not None and min_usd <= value <= max_usd

def within_inr_band(value: Optional[int], min_inr: int, max_inr: int) -> bool:
    """Legacy INR band check - kept for backward compatibility."""
    return value is not None and min_inr <= value <= max_inr


def _get_drive_service():
    global _DRIVE_SERVICE, _DRIVE_INIT_ATTEMPTED
    if not _DRIVE_SUPPORTED:
        return None
    if _DRIVE_SERVICE is not None:
        return _DRIVE_SERVICE
    if _DRIVE_INIT_ATTEMPTED:
        return None
    _DRIVE_INIT_ATTEMPTED = True
    try:
        _, drive_service = create_google_clients() if create_google_clients else (None, None)
        _DRIVE_SERVICE = drive_service
        if drive_service:
            log("✅ Google Drive service initialised for crawler uploads")
        return drive_service
    except Exception as exc:  # pragma: no cover - best effort logging
        log(f"⚠️ Failed to initialise Google Drive service: {exc}")
        return None


def upload_csv_to_drive(csv_path: str, folder_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    service = _get_drive_service()
    if not service or not os.path.exists(csv_path):
        return None
    metadata: Dict[str, Any] = {"name": os.path.basename(csv_path)}
    if folder_id:
        metadata["parents"] = [folder_id]
    try:
        media = MediaFileUpload(csv_path, mimetype="text/csv", resumable=False)  # type: ignore[arg-type]
        file = service.files().create(body=metadata, media_body=media, fields="id, webViewLink").execute()
        log(f"📁 Uploaded crawler CSV to Drive (id={file.get('id')})")
        return {"id": file.get("id"), "webViewLink": file.get("webViewLink")}
    except HttpError as http_err:  # type: ignore[call-arg]
        log(f"⚠️ Google Drive upload failed: {http_err}")
        return None
    except Exception as exc:
        log(f"⚠️ Unexpected error uploading to Drive: {exc}")
        return None


def extract_asha_project_details(project_url: str) -> Optional[Dict[str, Any]]:
    """Extract detailed information from an Asha project page."""
    try:
        response = get(project_url)
        if not response:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract project details
        project_data = {
            "title": "",
            "organization": "",
            "location": "",
            "status": "",
            "last_funding_amount": None,
            "last_funding_date": "",
            "steward_chapter": "",
            "description": ""
        }

        # Try to extract title
        title_elem = soup.find("h1") or soup.find("title")
        if title_elem:
            project_data["title"] = title_elem.get_text(strip=True)

        # Extract funding information from tables or text
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
                        # Try to extract amount
                        amount_match = re.search(r'(\d+[\d,]*)', value.replace(",", ""))
                        if amount_match:
                            project_data["last_funding_amount"] = int(amount_match.group(1))
                    elif "date" in key:
                        project_data["last_funding_date"] = value
                    elif "chapter" in key or "steward" in key:
                        project_data["steward_chapter"] = value

        # Extract description from paragraphs
        description_parts = []
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 50:  # Only include substantial paragraphs
                description_parts.append(text)

        project_data["description"] = " ".join(description_parts[:3])  # First 3 paragraphs

        return project_data

    except Exception as e:
        log(f"Error extracting project details from {project_url}: {e}")
        return None

def crawl(seed_urls: List[str], max_pages: int, delay_sec: float) -> List[str]:
    from collections import deque

    seen = set(seed_urls)
    queue = deque(seed_urls)
    documents: List[str] = []
    project_pages: List[str] = []
    pages = 0

    while queue and pages < max_pages:
        try:
            url = queue.popleft()
            if not is_allowed(url):
                continue

            response = get(url)
            time.sleep(delay_sec)
            if not response:
                continue

            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                if looks_like_doc(url):
                    documents.append(url)
                continue

            pages += 1
            log(f"Crawling page {pages}/{max_pages}: {url}")

            for link in absolute_links(url, response.text):
                if not is_allowed(link) or link in seen:
                    continue
                seen.add(link)

                # Check if it's an individual project page
                if "/project/?pid=" in link:
                    project_pages.append(link)
                elif looks_like_doc(link):
                    documents.append(link)
                else:
                    queue.append(link)

        except Exception as e:
            logging.error(f"An error occurred during crawling: {e}")

    # Return both documents and project pages for processing
    all_items = list(dict.fromkeys(documents + project_pages))
    log(f"Found {len(documents)} documents and {len(project_pages)} project pages")
    return all_items


def run(
    out_dir: str = "./out",
    min_usd: float = settings.DEFAULT_MIN_USD,
    max_usd: float = settings.DEFAULT_MAX_USD,
    usd_rate: float = settings.DEFAULT_USD_RATE,
    max_pages: int = settings.DEFAULT_MAX_PAGES,
    delay_sec: float = settings.DEFAULT_DELAY_SEC,
    seeds: Optional[List[str]] = None,
    upload_to_drive: bool = False,
    drive_folder_id: Optional[str] = None,
    return_details: bool = False,
    # Legacy INR parameters for backward compatibility
    min_inr: Optional[int] = None,
    max_inr: Optional[int] = None,
) -> RunResult | str:
    try:
        # Handle backward compatibility for INR parameters
        if min_inr is not None and max_inr is not None:
            min_usd = min_inr / usd_rate
            max_usd = max_inr / usd_rate
            log(f"Using legacy INR parameters: ₹{min_inr:,} - ₹{max_inr:,} (${min_usd:,.0f} - ${max_usd:,.0f})")

        seed_urls = seeds or settings.SEEDS
        download_dir = os.path.join(out_dir, "downloads")
        os.makedirs(download_dir, exist_ok=True)

        log(f"Starting Asha crawl with budget range: ${min_usd:,.0f} - ${max_usd:,.0f}")
        document_links = crawl(seed_urls, max_pages, delay_sec)
        log(f"Crawl finished. Found {len(document_links)} documents.")
        rows: List[Dict[str, Any]] = []

        for i, link in enumerate(document_links):
            log(f"Processing item {i+1}/{len(document_links)}: {link}")

            # Check if it's a project page or document
            if "/project/?pid=" in link:
                # Extract project details from Asha project page
                project_data = extract_asha_project_details(link)
                if not project_data:
                    continue

                # Convert INR to USD if amount is available
                amount_inr = project_data.get("last_funding_amount")
                amount_usd = amount_inr / usd_rate if amount_inr else None

                # Extract year from date if available
                year = None
                date_str = project_data.get("last_funding_date", "")
                year_match = re.search(r'20[0-2][0-9]', date_str)
                if year_match:
                    year = int(year_match.group())

                record = ProposalRecord(
                    title=project_data.get("title", "Unknown Project"),
                    org=project_data.get("organization", ""),
                    year=year,
                    chapter_or_funder=project_data.get("steward_chapter", "Asha"),
                    currency="USD" if amount_usd else "",
                    amount_requested_usd=amount_usd,
                    amount_inr=amount_inr,
                    link=link,
                    file_path="",  # No file for project pages
                    focus_area="Education",  # Default for Asha projects
                    geography=project_data.get("location", ""),
                    duration_months=None,
                    notes=f"Status: {project_data.get('status', '')}; {project_data.get('description', '')[:200]}...",
                )

                # Filter by USD amount for consistency
                if amount_usd is None or within_band(amount_usd, min_usd, max_usd):
                    rows.append(asdict(record))

            else:
                # Process as document (original logic)
                file_path = download_file(link, download_dir)
                if not file_path:
                    continue
                text = parse_pdf_text(file_path)
                amount_inr, amount_usd, note = pick_amount_from_text(text, usd_rate)
                year = guess_year(text)

                record = ProposalRecord(
                    title=os.path.basename(file_path),
                    org="",
                    year=year,
                    chapter_or_funder="Asha",
                    currency="USD" if amount_usd else "",
                    amount_requested_usd=amount_usd,
                    amount_inr=amount_inr,
                    link=link,
                    file_path=file_path,
                    focus_area="",
                    geography="",
                    duration_months=None,
                    notes=note,
                )

                # Filter by USD amount for consistency
                if within_band(amount_usd, min_usd, max_usd):
                    rows.append(asdict(record))

        log(f"Finished processing documents. Found {len(rows)} matching proposals.")
        csv_path = os.path.join(out_dir, "proposals.csv")
        log(f"Saving results to {csv_path}")
        fieldnames = list(rows[0].keys()) if rows else ["title", "amount_requested_usd", "amount_inr", "link", "notes"]

        with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            if rows:
                writer.writerows(rows)

        drive_info: Optional[Dict[str, Any]] = None
        target_folder = drive_folder_id or os.environ.get("FUNDINGBOT_DRIVE_FOLDER_ID")
        if upload_to_drive and target_folder:
            drive_info = upload_csv_to_drive(csv_path, target_folder)

        result = RunResult(
            csv_path=csv_path,
            rows=rows,
            uploaded_to_drive=bool(drive_info),
            drive_file_id=(drive_info or {}).get("id"),
            drive_web_link=(drive_info or {}).get("webViewLink"),
            drive_folder_id=target_folder,
        )

        return result if return_details else result.csv_path
    except Exception as e:
        logging.error(f"An error occurred during the run: {e}")
        return RunResult(csv_path="", rows=[]) if return_details else ""

