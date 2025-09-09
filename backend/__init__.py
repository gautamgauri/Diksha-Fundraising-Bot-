"""
Shared Backend Package for Diksha Foundation Fundraising Bot
Provides core functionality for both Slack and Web UI interfaces
"""

from .core import (
    EmailGenerator,
    DeepSeekClient,
    SheetsDB,
    create_google_clients,
    CacheManager
)

from .services import (
    DonorService,
    EmailService,
    PipelineService,
    TemplateService
)

from .context import ContextHelpers
from .backend_manager import BackendManager, backend_manager

__version__ = "1.0.0"
__all__ = [
    "EmailGenerator",
    "DeepSeekClient", 
    "SheetsDB",
    "create_google_clients",
    "CacheManager",
    "DonorService",
    "EmailService",
    "PipelineService",
    "TemplateService",
    "ContextHelpers",
    "BackendManager",
    "backend_manager"
]
