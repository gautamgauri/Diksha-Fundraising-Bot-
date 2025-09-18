# USAID-specific crawler settings - Primary repositories

# Primary USAID document repositories with specific search queries
USAID_SEEDS = [
    "https://decfinder.devme.ai/",  # Third-party DEC mirror with search
    "https://data.usaid.gov/",  # Development Data Library (DDL)
    "https://catalog.data.gov/dataset?organization=usaid-gov",  # Data.gov USAID datasets
]

# Specific search URLs for targeted document discovery
USAID_SEARCH_URLS = [
    "https://decfinder.devme.ai/search?q=education",
    "https://decfinder.devme.ai/search?q=youth",
    "https://decfinder.devme.ai/search?q=primary+education",
    "https://decfinder.devme.ai/search?q=vocational+training",
    "https://decfinder.devme.ai/search?q=children",
]

USAID_ALLOWED_DOMAINS = {
    "dec.usaid.gov",           # Development Experience Clearinghouse
    "data.usaid.gov",          # Development Data Library
    "foreignassistance.gov",   # Foreign assistance data
    "catalog.data.gov",        # Data.gov USAID datasets
    "decfinder.devme.ai",      # Third-party DEC mirror (backup)
}

# Document extensions for USAID documents
USAID_DOC_EXTS = {".pdf", ".doc", ".docx", ".txt", ".html"}

# User agent for USAID crawling
USAID_USER_AGENT = "Mozilla/5.0 (compatible; FundingBot/usaid-crawler; +https://example.org)"

# Education/Youth theme detection keywords
EDUCATION_KEYWORDS = {
    "education", "educational", "school", "schools", "literacy", "learning",
    "academic", "academics", "student", "students", "teacher", "teachers",
    "curriculum", "classroom", "instruction", "pedagogical", "scholarship",
    "university", "college", "training", "capacity building", "skills development"
}

YOUTH_KEYWORDS = {
    "youth", "youths", "adolescent", "adolescents", "young", "children",
    "child", "teenage", "teenager", "pupils", "minors", "juvenile",
    "early childhood", "primary school", "secondary school", "high school"
}

# Budget constraints for USAID (USD focus)
MAX_USD_BUDGET = 100_000
MIN_USD_BUDGET = 1_000  # Minimum threshold to filter out very small amounts

# USAID-specific crawling parameters
DEFAULT_USAID_MAX_PAGES = 200
DEFAULT_USAID_DELAY_SEC = 1.0  # Slightly slower for USAID sites
DEFAULT_USAID_USD_RATE = 1.0  # Base USD rate

# Document type priorities for USAID
USAID_PRIORITY_DOC_TYPES = {
    "proposal", "grant", "award", "funding", "project", "evaluation",
    "assessment", "report", "technical", "implementation"
}

# Regional focus (optional filtering)
USAID_REGIONS = {
    "africa", "asia", "latin america", "middle east", "global", "worldwide"
}