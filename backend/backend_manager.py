#!/usr/bin/env python3
"""
Backend Manager - Centralized initialization and management of all backend services
"""

import os
import logging
from typing import Optional, Dict, Any

from .core.email_generator import EmailGenerator
from .core.deepseek_client import DeepSeekClient
from .core.sheets_db import SheetsDB
from .core.google_auth import create_google_clients
from .core.cache_manager import cache_manager

from .services.donor_service import DonorService
from .services.email_service import EmailService
from .services.pipeline_service import PipelineService
from .services.template_service import TemplateService

from .context.context_helpers import ContextHelpers

logger = logging.getLogger(__name__)

class BackendManager:
    """Centralized backend manager for all services"""
    
    def __init__(self):
        """Initialize all backend services"""
        self.sheets_db = None
        self.email_generator = None
        self.deepseek_client = None
        self.drive_service = None
        self.google_auth = create_google_clients  # Reference to the function
        self.cache_manager = cache_manager  # Global cache manager instance
        
        # Services
        self.donor_service = None
        self.email_service = None
        self.pipeline_service = None
        self.template_service = None
        self.context_helpers = None
        
        # Status
        self.initialized = False
        self.initialization_errors = []
        
        # Initialize all services
        self._initialize_all()
    
    def _initialize_all(self):
        """Initialize all backend services"""
        try:
            logger.info("🚀 Initializing backend services...")
            
            # Initialize Google services
            self._initialize_google_services()
            
            # Initialize core services
            self._initialize_core_services()
            
            # Initialize business services
            self._initialize_business_services()
            
            # Check initialization status
            self._check_initialization_status()
            
        except Exception as e:
            logger.error(f"❌ Backend initialization failed: {e}")
            self.initialization_errors.append(str(e))
    
    def _initialize_google_services(self):
        """Initialize Google Sheets and Drive services"""
        try:
            # Create Google API clients
            self.sheets_service, self.drive_service = create_google_clients()
            
            if self.sheets_service and self.drive_service:
                logger.info("✅ Google API clients initialized")
            else:
                logger.warning("⚠️ Google API clients not available")
                
        except Exception as e:
            logger.error(f"❌ Google services initialization failed: {e}")
            self.initialization_errors.append(f"Google services: {e}")
    
    def _initialize_core_services(self):
        """Initialize core backend services"""
        try:
            # Initialize SheetsDB
            self.sheets_db = SheetsDB()
            if self.sheets_db.initialized:
                logger.info("✅ SheetsDB initialized")
            else:
                logger.warning("⚠️ SheetsDB not initialized")
            
            # Initialize EmailGenerator with Drive service
            self.email_generator = EmailGenerator(drive_service=self.drive_service)
            logger.info("✅ EmailGenerator initialized")
            
            # Initialize DeepSeek client
            self.deepseek_client = DeepSeekClient()
            if self.deepseek_client.initialized:
                logger.info("✅ DeepSeek client initialized")
            else:
                logger.warning("⚠️ DeepSeek client not initialized")
                
        except Exception as e:
            logger.error(f"❌ Core services initialization failed: {e}")
            self.initialization_errors.append(f"Core services: {e}")
    
    def _initialize_business_services(self):
        """Initialize business logic services"""
        try:
            # Initialize services with dependencies
            self.donor_service = DonorService(sheets_db=self.sheets_db)
            self.email_service = EmailService(
                email_generator=self.email_generator,
                sheets_db=self.sheets_db
            )
            self.pipeline_service = PipelineService(sheets_db=self.sheets_db)
            self.template_service = TemplateService(email_generator=self.email_generator)
            self.context_helpers = ContextHelpers(
                sheets_db=self.sheets_db,
                email_generator=self.email_generator
            )
            
            logger.info("✅ Business services initialized")
            
        except Exception as e:
            logger.error(f"❌ Business services initialization failed: {e}")
            self.initialization_errors.append(f"Business services: {e}")
    
    def _check_initialization_status(self):
        """Check overall initialization status"""
        critical_services = [
            ("SheetsDB", self.sheets_db and self.sheets_db.initialized),
            ("EmailGenerator", self.email_generator is not None),
            ("DonorService", self.donor_service is not None),
            ("EmailService", self.email_service is not None),
            ("PipelineService", self.pipeline_service is not None),
            ("TemplateService", self.template_service is not None),
            ("ContextHelpers", self.context_helpers is not None)
        ]
        
        failed_services = [name for name, status in critical_services if not status]
        
        if not failed_services:
            self.initialized = True
            logger.info("✅ All critical services initialized successfully")
        else:
            logger.warning(f"⚠️ Some services failed to initialize: {failed_services}")
            self.initialized = len(failed_services) <= 2  # Allow some non-critical failures
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all services"""
        return {
            "initialized": self.initialized,
            "initialization_errors": self.initialization_errors,
            "services": {
                "sheets_db": {
                    "available": self.sheets_db is not None,
                    "initialized": self.sheets_db.initialized if self.sheets_db else False
                },
                "email_generator": {
                    "available": self.email_generator is not None,
                    "mode": self.email_generator.get_mode() if self.email_generator else None
                },
                "deepseek_client": {
                    "available": self.deepseek_client is not None,
                    "initialized": self.deepseek_client.initialized if self.deepseek_client else False
                },
                "drive_service": {
                    "available": self.drive_service is not None
                },
                "donor_service": {
                    "available": self.donor_service is not None
                },
                "email_service": {
                    "available": self.email_service is not None
                },
                "pipeline_service": {
                    "available": self.pipeline_service is not None
                },
                "template_service": {
                    "available": self.template_service is not None
                },
                "context_helpers": {
                    "available": self.context_helpers is not None
                }
            },
            "environment": {
                "google_credentials": "configured" if os.environ.get("GOOGLE_CREDENTIALS_BASE64") else "missing",
                "anthropic_api_key": "configured" if os.environ.get("ANTHROPIC_API_KEY") else "missing",
                "deepseek_api_key": "configured" if os.environ.get("DEEPSEEK_API_KEY") else "missing"
            }
        }
    
    def get_services(self) -> Dict[str, Any]:
        """Get all initialized services"""
        return {
            "sheets_db": self.sheets_db,
            "email_generator": self.email_generator,
            "deepseek_client": self.deepseek_client,
            "drive_service": self.drive_service,
            "donor_service": self.donor_service,
            "email_service": self.email_service,
            "pipeline_service": self.pipeline_service,
            "template_service": self.template_service,
            "context_helpers": self.context_helpers
        }

# Global backend manager instance
backend_manager = BackendManager()
