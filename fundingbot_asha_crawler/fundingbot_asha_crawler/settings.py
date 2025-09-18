
SEEDS = [
    "https://ashanet.org/projects-list/",
]

ALLOWED_DOMAINS = {
    "ashanet.org",
    "documents.ashanet.org",
    "ashadocserver.s3.amazonaws.com",
}

DOC_EXTS = {".pdf", ".doc", ".docx"}

USER_AGENT = "Mozilla/5.0 (compatible; FundingBot/asha-crawler; +https://example.org)"
DEFAULT_USD_RATE = 83.0

# USD-based thresholds for consistency with USAID crawler
DEFAULT_MIN_USD = 30_000  # ~₹25L at 83 INR/USD
DEFAULT_MAX_USD = 50_000  # ~₹42L at 83 INR/USD

# Legacy INR values (for reference)
DEFAULT_MIN_INR = 2_500_000
DEFAULT_MAX_INR = 4_200_000

DEFAULT_DELAY_SEC = 0.8
DEFAULT_MAX_PAGES = 400
