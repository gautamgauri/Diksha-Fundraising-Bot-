"""
Donor Profile Generator Service
Extracted from Colab code for production use
"""

import os
import json
import time
import base64
import tempfile
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import re
from urllib.parse import urlencode, quote_plus
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ModelManager:
    """Manages AI models for profile generation and evaluation"""

    def __init__(self):
        self.models = {}
        self.logger = logging.getLogger(__name__)
        self._load_models()
    
    def _load_models(self):
        """Load available AI models based on environment variables"""
        # Anthropic models - use lazy initialization like email generator
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key and self._validate_api_key(anthropic_key):
            # Store the key for lazy initialization instead of creating client now
            self.models['anthropic'] = {
                'api_key': anthropic_key,
                'models': ['claude-3-5-sonnet-20241022', 'claude-3-haiku-20240307'],
                'type': 'anthropic',
                'client': None  # Will be initialized when needed
            }
            self.logger.info("Anthropic API key configured - client will be initialized when needed")

        # OpenAI models
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and self._validate_api_key(openai_key):
            try:
                import openai
                client = openai.OpenAI(api_key=openai_key)
                self.models['openai'] = {
                    'client': client,
                    'models': ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo'],
                    'type': 'openai'
                }
                self.logger.info("OpenAI models loaded successfully")
            except ImportError:
                self.logger.warning("OpenAI not available - install openai package")
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI client: {e}")

        # Google Gemini models
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_AI_API_KEY")
        if gemini_key and self._validate_api_key(gemini_key):
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                self.models['gemini'] = {
                    'client': genai,
                    'models': ['gemini-1.5-pro', 'gemini-1.5-flash'],
                    'type': 'gemini'
                }
                self.logger.info("Google Gemini models loaded successfully")
            except ImportError:
                self.logger.warning("Google Gemini not available - install google-generativeai package")
            except Exception as e:
                self.logger.error(f"Failed to initialize Gemini client: {e}")

        # Deepseek models
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key and self._validate_api_key(deepseek_key):
            try:
                import openai  # Deepseek uses OpenAI-compatible API
                client = openai.OpenAI(
                    api_key=deepseek_key,
                    base_url="https://api.deepseek.com"
                )
                self.models['deepseek'] = {
                    'client': client,
                    'models': ['deepseek-chat', 'deepseek-coder'],
                    'type': 'deepseek'
                }
                self.logger.info("Deepseek models loaded successfully")
            except ImportError:
                self.logger.warning("OpenAI package required for Deepseek - install openai package")
            except Exception as e:
                self.logger.error(f"Failed to initialize Deepseek client: {e}")

    def _validate_api_key(self, api_key: str) -> bool:
        """Basic API key validation"""
        return api_key and len(api_key.strip()) > 10 and not api_key.startswith('your-')
    
    def get_available_models(self) -> Dict:
        """Return available models"""
        return self.models
    
    def select_best_generation_model(self):
        """Select the best model for profile generation"""
        if 'anthropic' in self.models:
            return ('anthropic', 'claude-3-5-sonnet-20241022')
        elif 'openai' in self.models:
            return ('openai', 'gpt-4o')
        elif 'gemini' in self.models:
            return ('gemini', 'gemini-1.5-pro')
        elif 'deepseek' in self.models:
            return ('deepseek', 'deepseek-chat')
        else:
            self.logger.warning("No AI models available for profile generation")
            return None
    
    def select_best_evaluation_model(self):
        """Select the best model for profile evaluation"""
        if 'anthropic' in self.models:
            return ('anthropic', 'claude-3-haiku-20240307')
        elif 'openai' in self.models:
            return ('openai', 'gpt-4o-mini')
        elif 'gemini' in self.models:
            return ('gemini', 'gemini-1.5-flash')
        elif 'deepseek' in self.models:
            return ('deepseek', 'deepseek-chat')
        else:
            self.logger.warning("No AI models available for profile evaluation")
            return None


class DataCollector:
    """Collects research data about donors from various sources"""

    def __init__(self):
        self.session = requests.Session()

        # Set up retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Updated User-Agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        self.logger = logging.getLogger(__name__)

        # Initialize search services with quota tracking
        self.search_services = self._init_search_services()
    
    def get_foundation_website(self, donor_name: str) -> str:
        """Get foundation website URL using smart service fallback"""
        search_queries = [
            f'"{donor_name}" foundation website',
            f'{donor_name} foundation official site',
            f'{donor_name} foundation .org'
        ]

        # Try each query with available services
        for query in search_queries:
            attempts = 0
            max_attempts = len([s for s in self.search_services.values() if s.get('enabled')])

            while attempts < max_attempts:
                service_name = self._get_next_available_service()
                if not service_name:
                    break

                try:
                    self.logger.info(f"🔍 Trying {service_name} for: {query[:50]}...")
                    url = self._search_with_service(service_name, query)
                    if url:
                        self.logger.info(f"✅ Found URL using {service_name}: {url}")
                        return url

                except Exception as e:
                    error_msg = str(e)
                    if self._is_quota_error(service_name, error_msg):
                        self._mark_service_exhausted(service_name, error_msg)
                    else:
                        self.logger.error(f"❌ {service_name} search failed: {error_msg}")

                attempts += 1

        # Final fallback: domain guessing
        self.logger.info("🎯 Falling back to domain guessing")
        return self._guess_foundation_domain(donor_name)

    def _search_with_service(self, service_name: str, query: str) -> str:
        """Route search to appropriate service method"""
        search_methods = {
            'scaleserp': self._search_with_scaleserp,
            'valueserp': self._search_with_valueserp,
            'zenserp': self._search_with_zenserp,
            'bing': self._search_with_bing,
            'serpapi': self._search_with_serpapi,
            'searchapi': self._search_with_searchapi,
            'rapidapi_google': self._search_with_rapidapi,
            'wikipedia': self._search_with_wikipedia
            # 'duckduckgo': self._search_with_duckduckgo  # Disabled - too limited
        }

        if service_name in search_methods:
            return search_methods[service_name](query)
        return ""

    def _search_with_scaleserp(self, query: str) -> str:
        """Search using ScaleSerp"""
        try:
            url = "https://api.scaleserp.com/search"
            params = {
                'q': query,
                'api_key': self.search_services['scaleserp']['key'],
                'search_type': 'web',
                'num': 5
            }
            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'error' in data or 'message' in data:
                    error_msg = data.get('error', data.get('message', ''))
                    if self._is_quota_error('scaleserp', error_msg):
                        raise Exception(f"ScaleSerp quota exhausted: {error_msg}")

                for result in data.get('organic_results', []):
                    link = result.get('link', '')
                    if self._is_foundation_url(link):
                        return link
            else:
                if response.status_code in [429, 403, 402]:
                    raise Exception(f"ScaleSerp quota error: HTTP {response.status_code}")

        except Exception as e:
            if self._is_quota_error('scaleserp', str(e)):
                raise
            self.logger.error(f"ScaleSerp search failed: {e}")
        return ""

    def _search_with_valueserp(self, query: str) -> str:
        """Search using ValueSerp"""
        try:
            url = "https://api.valueserp.com/search"
            params = {
                'q': query,
                'api_key': self.search_services['valueserp']['key'],
                'search_type': 'web',
                'num': 5
            }
            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'error' in data:
                    error_msg = data['error']
                    if self._is_quota_error('valueserp', error_msg):
                        raise Exception(f"ValueSerp quota exhausted: {error_msg}")

                for result in data.get('organic_results', []):
                    link = result.get('link', '')
                    if self._is_foundation_url(link):
                        return link
            else:
                if response.status_code in [429, 403, 402]:
                    raise Exception(f"ValueSerp quota error: HTTP {response.status_code}")

        except Exception as e:
            if self._is_quota_error('valueserp', str(e)):
                raise
            self.logger.error(f"ValueSerp search failed: {e}")
        return ""

    def _search_with_zenserp(self, query: str) -> str:
        """Search using Zenserp"""
        try:
            url = "https://zenserp.com/api/v2/search"
            params = {
                'q': query,
                'apikey': self.search_services['zenserp']['key'],
                'search_engine': 'google.com',
                'num': 5
            }
            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'error' in data:
                    error_msg = data['error'].get('message', str(data['error']))
                    if self._is_quota_error('zenserp', error_msg):
                        raise Exception(f"Zenserp quota exhausted: {error_msg}")

                for result in data.get('organic', []):
                    link = result.get('url', '')
                    if self._is_foundation_url(link):
                        return link
            else:
                if response.status_code in [429, 403, 402]:
                    raise Exception(f"Zenserp quota error: HTTP {response.status_code}")

        except Exception as e:
            if self._is_quota_error('zenserp', str(e)):
                raise
            self.logger.error(f"Zenserp search failed: {e}")
        return ""

    def _search_with_serpapi(self, query: str) -> str:
        """Search using SerpAPI"""
        try:
            url = "https://serpapi.com/search"
            params = {
                'q': query,
                'api_key': self.search_services['serpapi']['key'],
                'engine': 'google',
                'num': 5
            }
            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'error' in data:
                    error_msg = data['error']
                    if self._is_quota_error('serpapi', error_msg):
                        raise Exception(f"SerpAPI quota exhausted: {error_msg}")

                for result in data.get('organic_results', []):
                    link = result.get('link', '')
                    if self._is_foundation_url(link):
                        return link
            else:
                if response.status_code in [429, 403, 402]:
                    raise Exception(f"SerpAPI quota error: HTTP {response.status_code}")

        except Exception as e:
            if self._is_quota_error('serpapi', str(e)):
                raise
            self.logger.error(f"SerpAPI search failed: {e}")
        return ""

    def _search_with_searchapi(self, query: str) -> str:
        """Search using SearchAPI"""
        try:
            url = "https://www.searchapi.io/api/v1/search"
            params = {
                'q': query,
                'api_key': self.search_services['searchapi']['key'],
                'engine': 'google',
                'num': 5
            }
            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                for result in data.get('organic_results', []):
                    link = result.get('link', '')
                    if self._is_foundation_url(link):
                        return link
            else:
                if response.status_code in [429, 403, 402]:
                    raise Exception(f"SearchAPI quota error: HTTP {response.status_code}")

        except Exception as e:
            if self._is_quota_error('searchapi', str(e)):
                raise
            self.logger.error(f"SearchAPI search failed: {e}")
        return ""

    def _search_with_rapidapi(self, query: str) -> str:
        """Search using RapidAPI Google Search"""
        try:
            url = "https://google-search3.p.rapidapi.com/api/v1/search"
            headers = {
                'X-RapidAPI-Key': self.search_services['rapidapi_google']['key'],
                'X-RapidAPI-Host': 'google-search3.p.rapidapi.com'
            }
            params = {'q': query, 'num': 5}
            response = self.session.get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                for result in data.get('results', []):
                    link = result.get('link', '')
                    if self._is_foundation_url(link):
                        return link
            else:
                if response.status_code in [429, 403, 402]:
                    raise Exception(f"RapidAPI quota error: HTTP {response.status_code}")

        except Exception as e:
            if self._is_quota_error('rapidapi_google', str(e)):
                raise
            self.logger.error(f"RapidAPI search failed: {e}")
        return ""

    def _search_with_bing(self, query: str) -> str:
        """Search using Bing Search API"""
        try:
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {
                'Ocp-Apim-Subscription-Key': self.search_services['bing']['key']
            }
            params = {
                'q': query,
                'count': 5,
                'responseFilter': 'Webpages'
            }
            response = self.session.get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                for result in data.get('webPages', {}).get('value', []):
                    link = result.get('url', '')
                    if self._is_foundation_url(link):
                        return link
            else:
                if response.status_code in [429, 403, 402]:
                    raise Exception(f"Bing quota error: HTTP {response.status_code}")

        except Exception as e:
            if self._is_quota_error('bing', str(e)):
                raise
            self.logger.error(f"Bing search failed: {e}")
        return ""

    def _search_with_duckduckgo(self, query: str) -> str:
        """Search using DuckDuckGo (free but limited)"""
        try:
            # Add rate limiting for free service
            time.sleep(1)

            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for result in data.get('Results', []):
                    first_url = result.get('FirstURL', '')
                    if self._is_foundation_url(first_url):
                        return first_url
        except Exception as e:
            self.logger.error(f"DuckDuckGo search failed: {e}")
        return ""

    def _search_with_wikipedia(self, query: str) -> str:
        """Search Wikipedia for foundation information and extract website"""
        try:
            # Add rate limiting for free service
            time.sleep(0.5)

            # Clean the query for better Wikipedia search
            donor_name = query.replace('"', '').replace(' foundation website', '').replace(' official site', '')

            # Try multiple Wikipedia search approaches
            search_terms = [
                donor_name,
                f"{donor_name} Foundation",
                f"{donor_name} Fund"
            ]

            for term in search_terms:
                try:
                    # Use Wikipedia API search
                    search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
                    encoded_term = quote_plus(term)
                    url = f"{search_url}{encoded_term}"

                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()

                        # Skip disambiguation pages
                        if data.get('type') == 'disambiguation':
                            continue

                        # Look for external links that might be the foundation website
                        page_url = data.get('content_urls', {}).get('desktop', {}).get('page', '')
                        if page_url:
                            # Get the full Wikipedia page to extract external links
                            wiki_content = self._extract_website_from_wikipedia(page_url)
                            if wiki_content and self._is_foundation_url(wiki_content):
                                return wiki_content

                except Exception as e:
                    self.logger.debug(f"Wikipedia search failed for {term}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Wikipedia search failed: {e}")

        return ""

    def _extract_website_from_wikipedia(self, wikipedia_url: str) -> str:
        """Extract official website URL from Wikipedia page"""
        try:
            # Get the Wikipedia page content
            response = self.session.get(wikipedia_url, timeout=10)
            if response.status_code != 200:
                return ""

            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for "Official website" in infobox or external links
            potential_urls = []

            # Check infobox for website
            infobox = soup.find('table', class_='infobox')
            if infobox:
                for row in infobox.find_all('tr'):
                    header = row.find('th')
                    if header and 'website' in header.get_text().lower():
                        link = row.find('a', href=True)
                        if link and link.get('href'):
                            href = link['href']
                            if href.startswith('http') and self._is_foundation_url(href):
                                potential_urls.append(href)

            # Check external links section
            external_links = soup.find('span', id='External_links')
            if external_links:
                section = external_links.find_parent()
                if section:
                    next_section = section.find_next_sibling()
                    if next_section and next_section.name == 'ul':
                        for link in next_section.find_all('a', href=True):
                            href = link.get('href', '')
                            if href.startswith('http') and self._is_foundation_url(href):
                                potential_urls.append(href)

            # Return the first valid foundation URL
            for url in potential_urls:
                if self._is_foundation_url(url):
                    return url

        except Exception as e:
            self.logger.debug(f"Failed to extract website from Wikipedia: {e}")

        return ""

    def _guess_foundation_domain(self, donor_name: str) -> str:
        """Fallback domain guessing method"""
        clean_name = donor_name.lower().replace(' ', '').replace('foundation', '').replace('fund', '')
        potential_domains = [
            f"{clean_name}.org",
            f"{clean_name}foundation.org",
            f"{clean_name}fund.org",
            f"www.{clean_name}.org",
            f"www.{clean_name}foundation.org"
        ]

        for domain in potential_domains:
            try:
                test_url = f"https://{domain}"
                response = self.session.head(test_url, timeout=5)
                if response.status_code == 200:
                    return test_url
            except Exception:
                continue
        return ""

    def _is_foundation_url(self, url: str) -> bool:
        """Check if URL likely belongs to a foundation"""
        if not url:
            return False

        url_lower = url.lower()
        foundation_indicators = [
            '.org/',
            'foundation',
            'fund',
            'charity',
            'nonprofit',
            'philanthrop'
        ]

        return any(indicator in url_lower for indicator in foundation_indicators)

    def _init_search_services(self) -> Dict[str, Any]:
        """Initialize available search and data services with quota tracking"""
        services = {}

        # ScaleSerp - 1000 free searches/month (best free tier)
        scaleserp_key = os.getenv("SCALESERP_API_KEY")
        if scaleserp_key and self._validate_api_key(scaleserp_key):
            services['scaleserp'] = {
                'key': scaleserp_key,
                'enabled': True,
                'quota_exhausted': False,
                'priority': 1,  # Highest priority due to generous free tier
                'free_limit': 1000,
                'error_codes': ['quota_exceeded', 'insufficient_balance']
            }
            self.logger.info("🔥 ScaleSerp configured (1000 free searches/month)")

        # ValueSerp - 1000 free searches/month
        valueserp_key = os.getenv("VALUESERP_API_KEY")
        if valueserp_key and self._validate_api_key(valueserp_key):
            services['valueserp'] = {
                'key': valueserp_key,
                'enabled': True,
                'quota_exhausted': False,
                'priority': 2,
                'free_limit': 1000,
                'error_codes': ['quota_exceeded', 'insufficient_credits']
            }
            self.logger.info("⚡ ValueSerp configured (1000 free searches/month)")

        # Zenserp - 1000 free searches/month
        zenserp_key = os.getenv("ZENSERP_API_KEY")
        if zenserp_key and self._validate_api_key(zenserp_key):
            services['zenserp'] = {
                'key': zenserp_key,
                'enabled': True,
                'quota_exhausted': False,
                'priority': 3,
                'free_limit': 1000,
                'error_codes': ['quota_exceeded', 'limit_reached']
            }
            self.logger.info("🔍 Zenserp configured (1000 free searches/month)")

        # Bing Search API - DEPRECATED (Microsoft retiring the service)
        # Keeping for backwards compatibility but with lower priority
        bing_key = os.getenv("BING_SEARCH_API_KEY")
        if bing_key and self._validate_api_key(bing_key):
            services['bing'] = {
                'key': bing_key,
                'enabled': True,
                'quota_exhausted': False,
                'priority': 8,  # Lower priority due to deprecation
                'free_limit': 1000,  # Reduced from original claim
                'error_codes': ['quota_exceeded', '403'],
                'deprecated': True
            }
            self.logger.warning("⚠️ Bing Search API configured but DEPRECATED - Microsoft is retiring this service")

        # SerpAPI - 100 free searches/month (highest quality)
        serpapi_key = os.getenv("SERPAPI_KEY")
        if serpapi_key and self._validate_api_key(serpapi_key):
            services['serpapi'] = {
                'key': serpapi_key,
                'enabled': True,
                'quota_exhausted': False,
                'priority': 4,  # Higher priority due to quality
                'free_limit': 100,
                'error_codes': ['quota_exceeded', 'insufficient_credits']
            }
            self.logger.info("🚀 SerpAPI configured (100 free searches/month)")

        # SearchAPI - 100 free searches/month
        searchapi_key = os.getenv("SEARCHAPI_KEY")
        if searchapi_key and self._validate_api_key(searchapi_key):
            services['searchapi'] = {
                'key': searchapi_key,
                'enabled': True,
                'quota_exhausted': False,
                'priority': 5,
                'free_limit': 100,
                'error_codes': ['quota_exceeded', 'credits_exhausted']
            }
            self.logger.info("📊 SearchAPI configured (100 free searches/month)")

        # Add RapidAPI alternatives
        rapidapi_key = os.getenv("RAPIDAPI_KEY")
        if rapidapi_key and self._validate_api_key(rapidapi_key):
            services['rapidapi_google'] = {
                'key': rapidapi_key,
                'enabled': True,
                'quota_exhausted': False,
                'priority': 6,
                'free_limit': 500,  # Varies by provider
                'error_codes': ['quota_exceeded', 'subscription_required']
            }
            self.logger.info("⚡ RapidAPI Google Search configured (500+ free searches/month)")

        # DuckDuckGo disabled - API is too limited for foundation search
        # services['duckduckgo'] = {
        #     'enabled': False,
        #     'quota_exhausted': False,
        #     'priority': 7,
        #     'free_limit': float('inf')
        # }
        # Wikipedia - excellent for background info on major foundations
        services['wikipedia'] = {
            'enabled': True,
            'quota_exhausted': False,
            'priority': 8,  # Higher priority - very useful for foundation info
            'free_limit': float('inf')
        }

        total_services = len([s for s in services.values() if s.get('enabled')])
        total_quota = sum([s.get('free_limit', 0) for s in services.values()
                          if isinstance(s.get('free_limit'), int)])

        self.logger.info(f"✅ Initialized {total_services} search services with {total_quota}+ total monthly searches")
        return services

    def _get_next_available_service(self) -> Optional[str]:
        """Get next available service based on priority and quota status"""
        available_services = [
            (name, config) for name, config in self.search_services.items()
            if config.get('enabled') and not config.get('quota_exhausted', False)
        ]

        # Sort by priority (lower number = higher priority)
        available_services.sort(key=lambda x: x[1].get('priority', 999))

        if available_services:
            service_name, config = available_services[0]
            return service_name

        self.logger.warning("⚠️ No search services available - all quotas exhausted")
        return None

    def _mark_service_exhausted(self, service_name: str, error_msg: str = ""):
        """Mark a service as quota exhausted"""
        if service_name in self.search_services:
            self.search_services[service_name]['quota_exhausted'] = True
            limit = self.search_services[service_name].get('free_limit', 'unknown')
            self.logger.warning(f"🔄 {service_name} quota exhausted (limit: {limit}). Switching to next service.")

    def _is_quota_error(self, service_name: str, error_msg: str, status_code: int = None) -> bool:
        """Check if error indicates quota exhaustion"""
        if service_name not in self.search_services:
            return False

        error_codes = self.search_services[service_name].get('error_codes', [])
        error_msg_lower = error_msg.lower()

        quota_indicators = [
            'quota', 'limit', 'exceeded', 'exhausted', 'credits', 'balance',
            'rate limit', 'too many requests', '429', 'forbidden'
        ]

        return (
            any(code in error_msg_lower for code in error_codes) or
            any(indicator in error_msg_lower for indicator in quota_indicators) or
            status_code in [429, 403, 402]
        )
    
    def scrape_foundation_page(self, url: str, max_content: int = 5000) -> Dict:
        """Scrape content from foundation website with improved error handling"""
        if not url:
            return {"success": False, "content": "", "error": "No URL provided"}

        try:
            # Add rate limiting
            time.sleep(1)  # Be respectful to websites

            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return {"success": False, "content": "", "error": f"HTTP {response.status_code}"}

            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'text/html' not in content_type.lower():
                return {"success": False, "content": "", "error": f"Invalid content type: {content_type}"}

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()

            # Extract text content
            text = soup.get_text(separator=' ', strip=True)

            # Clean and limit content
            text = re.sub(r'\s+', ' ', text).strip()
            if len(text) > max_content:
                text = text[:max_content] + "..."

            # Extract additional metadata
            meta_description = ''
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                meta_description = meta_tag.get('content', '')

            return {
                "success": True,
                "content": text,
                "url": url,
                "title": soup.title.string if soup.title else "",
                "meta_description": meta_description,
                "content_length": len(text)
            }

        except requests.exceptions.Timeout:
            return {"success": False, "content": "", "error": "Request timeout"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "content": "", "error": "Connection failed"}
        except Exception as e:
            self.logger.error(f"Scraping error for {url}: {e}")
            return {"success": False, "content": "", "error": str(e)}
    
    def conduct_web_scraping_research(self, donor_name: str) -> Dict:
        """Conduct comprehensive web research for donor"""
        print(f"🔍 Starting web research for: {donor_name}")
        
        research_data = {
            "donor_name": donor_name,
            "website_data": {},
            "additional_sources": [],
            "wikipedia_data": {},
            "services_used": [],
            "research_timestamp": datetime.now().isoformat()
        }
        
        # Get main website
        website_url = self.get_foundation_website(donor_name)
        if website_url:
            print(f"📄 Found website: {website_url}")
            website_data = self.scrape_foundation_page(website_url)
            research_data["website_data"] = website_data

        # Get Wikipedia information for additional context
        wikipedia_data = self._get_wikipedia_info(donor_name)
        if wikipedia_data:
            print(f"📚 Found Wikipedia info: {wikipedia_data.get('title', 'N/A')}")
            research_data["wikipedia_data"] = wikipedia_data
            research_data["services_used"].append("wikipedia")

        # Track which services were used and their status
        services_status = self.get_available_services()
        research_data["services_status"] = services_status

        return research_data

    def _get_wikipedia_info(self, donor_name: str) -> Dict:
        """Get comprehensive Wikipedia information for a foundation"""
        try:
            # Use Wikipedia API
            search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"

            # Try different search terms
            search_terms = [
                donor_name,
                f"{donor_name} Foundation",
                f"{donor_name} Fund",
                f"{donor_name} Charitable Foundation"
            ]

            for term in search_terms:
                try:
                    url = f"{search_url}{quote_plus(term)}"
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()

                        # Skip disambiguation pages
                        if data.get('type') == 'disambiguation':
                            continue

                        # Check if this looks like a foundation/organization
                        title = data.get('title', '').lower()
                        extract = data.get('extract', '').lower()

                        foundation_keywords = ['foundation', 'fund', 'charity', 'philanthropic', 'nonprofit', 'grants']
                        if any(keyword in title or keyword in extract for keyword in foundation_keywords):

                            # Get additional details from the full page
                            page_url = data.get('content_urls', {}).get('desktop', {}).get('page', '')
                            additional_info = self._get_wikipedia_details(page_url) if page_url else {}

                            return {
                                'title': data.get('title', ''),
                                'extract': data.get('extract', ''),
                                'url': page_url,
                                'source': 'wikipedia',
                                'thumbnail': data.get('thumbnail', {}).get('source', ''),
                                'founded': additional_info.get('founded', ''),
                                'headquarters': additional_info.get('headquarters', ''),
                                'website': additional_info.get('website', ''),
                                'type': additional_info.get('type', ''),
                                'focus_areas': additional_info.get('focus_areas', [])
                            }
                except Exception as e:
                    self.logger.debug(f"Wikipedia search failed for {term}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Wikipedia search failed: {e}")
        return {}

    def _get_wikipedia_details(self, wikipedia_url: str) -> Dict:
        """Extract additional details from Wikipedia page"""
        try:
            response = self.session.get(wikipedia_url, timeout=10)
            if response.status_code != 200:
                return {}

            soup = BeautifulSoup(response.content, 'html.parser')
            details = {}

            # Look for infobox data
            infobox = soup.find('table', class_='infobox')
            if infobox:
                for row in infobox.find_all('tr'):
                    header = row.find('th')
                    data_cell = row.find('td')

                    if header and data_cell:
                        header_text = header.get_text().strip().lower()
                        data_text = data_cell.get_text().strip()

                        # Map common infobox fields
                        if 'founded' in header_text or 'established' in header_text:
                            details['founded'] = data_text
                        elif 'headquarters' in header_text or 'location' in header_text:
                            details['headquarters'] = data_text
                        elif 'website' in header_text:
                            link = data_cell.find('a', href=True)
                            if link:
                                details['website'] = link.get('href', '')
                        elif 'type' in header_text:
                            details['type'] = data_text
                        elif 'focus' in header_text or 'areas' in header_text:
                            details['focus_areas'] = [area.strip() for area in data_text.split(',')]

            return details

        except Exception as e:
            self.logger.debug(f"Failed to extract Wikipedia details: {e}")
            return {}

    def get_available_services(self) -> Dict:
        """Get detailed status of search services"""
        status = {}
        for service, config in self.search_services.items():
            status[service] = {
                'enabled': config.get('enabled', False),
                'quota_exhausted': config.get('quota_exhausted', False),
                'priority': config.get('priority', 999),
                'free_limit': config.get('free_limit', 'N/A')
            }
        return status

    def reset_quota_flags(self):
        """Reset quota exhausted flags (call this monthly or when quotas reset)"""
        for service in self.search_services:
            self.search_services[service]['quota_exhausted'] = False
        self.logger.info("🔄 Reset all quota exhausted flags")

    def get_service_recommendations(self) -> List[str]:
        """Get recommended services to configure based on free limits"""
        recommendations = [
            "🔥 ScaleSerp (1000 free/month) - Best free tier",
            "⚡ ValueSerp (1000 free/month) - Good backup",
            "🔍 Zenserp (1000 free/month) - Another backup",
            "🚀 SerpAPI (100 free/month) - Highest quality",
            "📊 SearchAPI (100 free/month) - Good alternative",
            "⚡ RapidAPI Google (500+ free/month) - Multiple providers",
            "⚠️ Bing API (DEPRECATED) - Microsoft retiring service",
            "📚 Wikipedia (FREE) - Excellent for foundation background info",
            "❌ DuckDuckGo (DISABLED) - Too limited for foundation search"
        ]
        return recommendations


class ProfileGenerator:
    """Generates donor profiles using AI models"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
    
    def generate_profile(self, donor_name: str, research_data: Dict) -> Dict:
        """Generate a comprehensive donor profile"""
        provider, model = self.model_manager.select_best_generation_model()
        if not provider:
            return {"success": False, "error": "No AI models available"}
        
        # Prepare research context
        context = self._prepare_context(donor_name, research_data)
        
        # Generate profile using AI
        prompt = self._create_generation_prompt(donor_name, context)
        
        try:
            if provider == 'anthropic':
                response = self._generate_with_anthropic(model, prompt)
            elif provider == 'openai':
                response = self._generate_with_openai(model, prompt)
            elif provider == 'gemini':
                response = self._generate_with_gemini(model, prompt)
            elif provider == 'deepseek':
                response = self._generate_with_deepseek(model, prompt)
            else:
                return {"success": False, "error": f"Unsupported provider: {provider}"}
            
            return {
                "success": True,
                "profile": response,
                "model_used": f"{provider}/{model}",
                "generation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _prepare_context(self, donor_name: str, research_data: Dict) -> str:
        """Prepare research context for AI generation"""
        context_parts = [f"Research data for {donor_name}:"]
        
        if research_data.get("website_data", {}).get("content"):
            context_parts.append(f"Website content: {research_data['website_data']['content']}")
        
        return "\n\n".join(context_parts)
    
    def _create_generation_prompt(self, donor_name: str, context: str) -> str:
        """Create the AI prompt for profile generation"""
        return f"""
You are a professional fundraising researcher tasked with creating a comprehensive donor profile.

DONOR NAME: {donor_name}

RESEARCH CONTEXT:
{context}

Please create a detailed donor profile that includes:

1. **Executive Summary** (2-3 sentences overview)
2. **Organization Background** (history, mission, key activities)
3. **Financial Information** (assets, giving patterns, grant ranges)
4. **Leadership** (key personnel, board members if available)
5. **Focus Areas** (causes they support, geographic preferences)
6. **Engagement Strategy** (best approaches for outreach)
7. **Recent Activities** (recent grants, news, initiatives)
8. **Contact Information** (official channels, key contacts)

Format the response as a professional donor profile document with clear sections and actionable insights for fundraising teams.

Make sure to:
- Be factual and evidence-based
- Include specific details when available
- Highlight opportunities for engagement
- Note any limitations in available data
- Use professional, clear language suitable for fundraising staff
"""
    
    def _generate_with_anthropic(self, model: str, prompt: str) -> str:
        """Generate profile using Anthropic Claude"""
        # Lazy initialization of Anthropic client
        client = self._get_anthropic_client()
        if not client:
            raise Exception("Failed to initialize Anthropic client")
        
        message = client.messages.create(
            model=model,
            max_tokens=4000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
    
    def _get_anthropic_client(self):
        """Get or create Anthropic client with lazy initialization"""
        if 'anthropic' not in self.model_manager.models:
            return None
            
        anthropic_config = self.model_manager.models['anthropic']
        
        # Return existing client if already initialized
        if anthropic_config.get('client'):
            return anthropic_config['client']
        
        # Initialize client now
        try:
            import anthropic
            api_key = anthropic_config['api_key']
            
            # Try basic initialization first
            try:
                client = anthropic.Anthropic(api_key=api_key)
                self.model_manager.logger.info("Anthropic client initialized successfully")
            except Exception as e:
                self.model_manager.logger.warning(f"Basic Anthropic initialization failed: {e}")
                return None
            
            # Store the client for future use
            anthropic_config['client'] = client
            return client
            
        except ImportError:
            self.model_manager.logger.warning("Anthropic package not available")
            return None
        except Exception as e:
            self.model_manager.logger.error(f"Failed to initialize Anthropic client: {e}")
            return None

    def _generate_with_openai(self, model: str, prompt: str) -> str:
        """Generate profile using OpenAI GPT"""
        client = self.model_manager.models['openai']['client']
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
            temperature=0.3
        )
        
        return response.choices[0].message.content

    def _generate_with_gemini(self, model: str, prompt: str) -> str:
        """Generate profile using Google Gemini"""
        client = self.model_manager.models['gemini']['client']

        gemini_model = client.GenerativeModel(model)
        response = gemini_model.generate_content(prompt)

        return response.text

    def _generate_with_deepseek(self, model: str, prompt: str) -> str:
        """Generate profile using Deepseek"""
        client = self.model_manager.models['deepseek']['client']

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
            temperature=0.3
        )

        return response.choices[0].message.content


class ProfileEvaluator:
    """Evaluates profile quality and provides improvement suggestions"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
    
    def evaluate_profile(self, profile: str, donor_name: str) -> Dict:
        """Evaluate profile quality and provide score"""
        provider, model = self.model_manager.select_best_evaluation_model()
        if not provider:
            return {"success": False, "error": "No evaluation models available"}
        
        evaluation_prompt = self._create_evaluation_prompt(profile, donor_name)
        
        try:
            if provider == 'anthropic':
                response = self._evaluate_with_anthropic(model, evaluation_prompt)
            elif provider == 'openai':
                response = self._evaluate_with_openai(model, evaluation_prompt)
            elif provider == 'gemini':
                response = self._evaluate_with_gemini(model, evaluation_prompt)
            elif provider == 'deepseek':
                response = self._evaluate_with_deepseek(model, evaluation_prompt)
            else:
                return {"success": False, "error": f"Unsupported provider: {provider}"}
            
            score = self._extract_score(response)
            
            return {
                "success": True,
                "evaluation": response,
                "score": score,
                "model_used": f"{provider}/{model}",
                "evaluation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_evaluation_prompt(self, profile: str, donor_name: str) -> str:
        """Create evaluation prompt"""
        return f"""
Please evaluate this donor profile for {donor_name} on a scale of 1-100:

PROFILE TO EVALUATE:
{profile}

Evaluation Criteria:
1. Completeness (all key sections present)
2. Accuracy (factual, well-researched information)
3. Actionability (clear engagement strategies)
4. Professional presentation
5. Fundraising relevance

Please provide:
1. Overall Score (1-100)
2. Strengths of the profile
3. Areas for improvement
4. Specific suggestions for enhancement

Format: Start with "SCORE: [number]" then provide detailed feedback.
"""
    
    def _evaluate_with_anthropic(self, model: str, prompt: str) -> str:
        """Evaluate using Anthropic Claude"""
        # Lazy initialization of Anthropic client
        client = self._get_anthropic_client()
        if not client:
            raise Exception("Failed to initialize Anthropic client")
        
        message = client.messages.create(
            model=model,
            max_tokens=2000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
    
    def _evaluate_with_openai(self, model: str, prompt: str) -> str:
        """Evaluate using OpenAI GPT"""
        client = self.model_manager.models['openai']['client']
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.1
        )
        
        return response.choices[0].message.content
    
    def _extract_score(self, evaluation: str) -> int:
        """Extract numerical score from evaluation"""
        score_match = re.search(r'SCORE:\s*(\d+)', evaluation)
        if score_match:
            return int(score_match.group(1))
        
        # Fallback: look for any number between 1-100
        numbers = re.findall(r'\b(\d{1,3})\b', evaluation)
        for num in numbers:
            score = int(num)
            if 1 <= score <= 100:
                return score
        
        return 50  # Default score if none found


class GoogleDocsExporter:
    """Exports profiles to Google Docs"""
    
    def __init__(self, creds: Credentials):
        self.creds = creds
        self.docs_service = build('docs', 'v1', credentials=creds)
        self.drive_service = build('drive', 'v3', credentials=creds)
    
    def create_profile_document(self, donor_name: str, profile_content: str, 
                              folder_id: Optional[str] = None) -> Dict:
        """Create a Google Doc with the donor profile"""
        try:
            # Create document title
            doc_title = f"Donor Profile - {donor_name} - {datetime.now().strftime('%Y-%m-%d')}"
            
            # Create the document
            document = {
                'title': doc_title
            }
            
            doc = self.docs_service.documents().create(body=document).execute()
            doc_id = doc.get('documentId')
            
            # Add content to document
            self._add_content_to_doc(doc_id, profile_content)
            
            # Move to folder if specified
            if folder_id:
                self._move_to_folder(doc_id, folder_id)
            
            # Get document URL
            doc_url = f"https://docs.google.com/document/d/{doc_id}"
            
            return {
                "success": True,
                "document_id": doc_id,
                "document_url": doc_url,
                "title": doc_title
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _add_content_to_doc(self, doc_id: str, content: str):
        """Add formatted content to the document"""
        requests = [
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': content
                }
            }
        ]
        
        self.docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
    
    def _move_to_folder(self, doc_id: str, folder_id: str):
        """Move document to specified folder"""
        file = self.drive_service.files().get(fileId=doc_id, fields='parents').execute()
        previous_parents = ",".join(file.get('parents'))
        
        self.drive_service.files().update(
            fileId=doc_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()


class DonorProfileService:
    """Main service orchestrating donor profile generation"""

    def __init__(self):
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.model_manager = ModelManager()
        self.data_collector = DataCollector()
        self.profile_generator = ProfileGenerator(self.model_manager)
        self.profile_evaluator = ProfileEvaluator(self.model_manager)
        self.google_creds = None
        self.docs_exporter = None
        self._setup_google_auth()
    
    def _setup_google_auth(self):
        """Setup Google authentication"""
        try:
            # Try to get credentials from environment
            creds_b64 = os.getenv("GOOGLE_CREDENTIALS_BASE64")
            if creds_b64:
                creds_json = base64.b64decode(creds_b64).decode("utf-8")
                creds_data = json.loads(creds_json)
                
                scopes = [
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive',
                    'https://www.googleapis.com/auth/documents'
                ]
                
                self.google_creds = Credentials.from_service_account_info(creds_data, scopes=scopes)
                self.docs_exporter = GoogleDocsExporter(self.google_creds)
                self.logger.info("Google authentication configured")
            else:
                self.logger.warning("GOOGLE_CREDENTIALS_BASE64 not found in environment")
        except Exception as e:
            self.logger.error(f"Google auth setup failed: {e}")
    
    def generate_donor_profile(self, donor_name: str, export_to_docs: bool = True,
                             folder_id: Optional[str] = None) -> Dict:
        """Generate a complete donor profile"""
        if not donor_name or not donor_name.strip():
            return {"success": False, "error": "Donor name is required"}

        self.logger.info(f"Starting donor profile generation for: {donor_name}")

        results = {
            "donor_name": donor_name.strip(),
            "start_time": datetime.now().isoformat(),
            "steps": {}
        }

        try:
            # Check AI models (required)
            available_models = self.model_manager.get_available_models()
            if not available_models:
                return {
                    "success": False,
                    "error": "No AI models available. Please configure ANTHROPIC_API_KEY or OPENAI_API_KEY.",
                    "end_time": datetime.now().isoformat()
                }

            # Check search services (optional - log status but don't fail)
            available_search_services = [
                name for name, config in self.data_collector.search_services.items()
                if config.get('enabled') and not config.get('quota_exhausted', False)
            ]

            if not available_search_services:
                self.logger.warning("No search services available - will use domain guessing and Wikipedia only")
            else:
                self.logger.info(f"Available search services: {', '.join(available_search_services)}")

            # Step 1: Data Collection
            self.logger.info("Step 1: Collecting research data...")
            research_data = self.data_collector.conduct_web_scraping_research(donor_name)
            results["steps"]["research"] = {"success": True, "data": research_data}

            # Step 2: Profile Generation
            self.logger.info("Step 2: Generating donor profile...")
            generation_result = self.profile_generator.generate_profile(donor_name, research_data)
            if not generation_result["success"]:
                results["steps"]["generation"] = generation_result
                results["success"] = False
                results["end_time"] = datetime.now().isoformat()
                return results

            profile_content = generation_result["profile"]
            results["steps"]["generation"] = generation_result

            # Step 3: Profile Evaluation
            self.logger.info("Step 3: Evaluating profile quality...")
            evaluation_result = self.profile_evaluator.evaluate_profile(profile_content, donor_name)
            results["steps"]["evaluation"] = evaluation_result

            # Step 4: Export to Google Docs
            if export_to_docs and self.docs_exporter:
                self.logger.info("Step 4: Exporting to Google Docs...")
                export_result = self.docs_exporter.create_profile_document(
                    donor_name, profile_content, folder_id
                )
                results["steps"]["export"] = export_result

                if export_result["success"]:
                    results["document_url"] = export_result["document_url"]
                    results["document_id"] = export_result["document_id"]
            elif export_to_docs:
                results["steps"]["export"] = {
                    "success": False,
                    "error": "Google Docs exporter not configured"
                }

            results["success"] = True
            results["profile_content"] = profile_content
            results["end_time"] = datetime.now().isoformat()

            self.logger.info("Donor profile generation completed successfully!")
            return results

        except Exception as e:
            self.logger.error(f"Profile generation failed: {e}")
            results["success"] = False
            results["error"] = str(e)
            results["end_time"] = datetime.now().isoformat()
            return results
    
    def get_available_models(self) -> Dict:
        """Get information about available AI models"""
        return self.model_manager.get_available_models()
    
    def is_google_docs_available(self) -> bool:
        """Check if Google Docs export is available"""
        return self.docs_exporter is not None

    def get_search_service_status(self) -> Dict:
        """Get current status of all search services"""
        return self.data_collector.get_available_services()

    def reset_search_quotas(self):
        """Reset search service quotas (useful for monthly resets)"""
        self.data_collector.reset_quota_flags()

    def get_search_recommendations(self) -> List[str]:
        """Get recommendations for search services to configure"""
        return self.data_collector.get_service_recommendations()
