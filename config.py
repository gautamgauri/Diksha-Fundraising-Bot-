#!/usr/bin/env python3
"""
Configuration file for Diksha Foundation Fundraising Bot
"""

import os
from enum import Enum

class DeploymentMode(Enum):
    DEVELOPMENT = "dev"
    STAGING = "staging" 
    PRODUCTION = "prod"

# Email Generation Configuration
EMAIL_CONFIG = {
    'max_tokens': 1200,
    'temperature': 0.7,
    'similarity_threshold': 0.8,
    'content_length_limit': 2000,
    'profile_summary_limit': 500,
    'max_retries': 3,
    'retry_delay': 1
}

# Diksha Foundation Information
DIKSHA_INFO = {
    'youth_trained': '2,500+',
    'employment_rate': '85%',
    'founding_year': '2010',
    'location': 'Bihar',
    'programs': [
        'Digital Skills Training',
        'Youth Empowerment', 
        'Rural Education Access'
    ]
}

# Cache Configuration
CACHE_CONFIG = {
    'profile_timeout': 3600,  # 1 hour
    'max_cache_size': 50,
    'cleanup_interval': 1800   # 30 minutes
}

# API Configuration
API_CONFIG = {
    'claude_model': 'claude-sonnet-4-20250514',
    'max_request_size': 1000000,  # 1MB
    'timeout': 30
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'email_generator.log',
    'max_bytes': 10485760,  # 10MB
    'backup_count': 5
}

# Security Configuration
SECURITY_CONFIG = {
    'max_input_length': 200,
    'sanitize_inputs': True,
    'allowed_file_types': [
        'application/pdf',
        'application/vnd.google-apps.document'
    ]
}

# Get deployment mode from environment
DEPLOYMENT_MODE = DeploymentMode(os.environ.get('DEPLOYMENT_MODE', 'development').lower())

# Adjust settings based on deployment mode
if DEPLOYMENT_MODE == DeploymentMode.PRODUCTION:
    EMAIL_CONFIG['max_retries'] = 3
    CACHE_CONFIG['profile_timeout'] = 1800  # 30 minutes
    LOGGING_CONFIG['level'] = 'WARNING'
elif DEPLOYMENT_MODE == DeploymentMode.STAGING:
    EMAIL_CONFIG['max_retries'] = 2
    CACHE_CONFIG['profile_timeout'] = 900   # 15 minutes
    LOGGING_CONFIG['level'] = 'INFO'
else:  # DEVELOPMENT
    EMAIL_CONFIG['max_retries'] = 1
    CACHE_CONFIG['profile_timeout'] = 300   # 5 minutes
    LOGGING_CONFIG['level'] = 'DEBUG'
