#!/usr/bin/env python3
"""
Email Generator Module
Diksha Foundation Fundraising Bot
"""

import os
import logging
import re
import time
from typing import Tuple, Dict, Any, Optional
from functools import wraps, lru_cache
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from collections import defaultdict

# Import configuration
from config import (
    EMAIL_CONFIG, DIKSHA_INFO, CACHE_CONFIG, 
    API_CONFIG, SECURITY_CONFIG, DEPLOYMENT_MODE
)
from cache_manager import cache_manager

# Configure logging
logger = logging.getLogger(__name__)

def retry_on_failure(max_retries=None, delay=None):
    """Retry decorator with exponential backof"""
    max_retries = max_retries or EMAIL_CONFIG['max_retries']
    delay = delay or EMAIL_CONFIG['retry_delay']
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                        logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    else:
                        logger.error(f"All {max_retries} attempts failed: {e}")
            
            raise last_exception
        return wrapper
    return decorator

class RateLimiter:
    """Simple rate limiter for API calls"""
    def __init__(self, max_calls=10, time_window=60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> bool:
        now = time.time()
        # Clean old entries
        self.calls[identifier] = [
            call_time for call_time in self.calls[identifier] 
            if now - call_time < self.time_window
        ]
        
        if len(self.calls[identifier]) < self.max_calls:
            self.calls[identifier].append(now)
            return True
        return False

class EmailGenerator:
    """Modular email generator with template-based enhancement and Google Drive integration"""
    
    def __init__(self, drive_service=None):
        """Initialize the email generator"""
        self.claude_api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.enhancement_mode = "claude"  # Default mode
        self.drive_service = drive_service  # Google Drive service for donor profiles
        
        # Configuration from config file
        self.max_tokens = EMAIL_CONFIG['max_tokens']
        self.temperature = EMAIL_CONFIG['temperature']
        self.similarity_threshold = EMAIL_CONFIG['similarity_threshold']
        self.content_length_limit = EMAIL_CONFIG['content_length_limit']
        self.profile_summary_limit = EMAIL_CONFIG['profile_summary_limit']
        
        # Rate limiting
        self.rate_limiter = RateLimiter(
            max_calls=EMAIL_CONFIG.get('max_calls_per_minute', 10),
            time_window=60
        )
        
        # Log deployment mode
        logger.info(f"EmailGenerator initialized in {DEPLOYMENT_MODE.value} mode")
    
    def get_system_health(self) -> Dict[str, Any]:
        """Monitor system resources for small deployments"""
        try:
            import psutil
            cache_stats = cache_manager.get_stats()
            
            health_data = {
                'deployment_mode': DEPLOYMENT_MODE.value,
                'cache_stats': cache_stats,
                'claude_api_configured': bool(self.claude_api_key),
                'drive_service_configured': bool(self.drive_service),
                'rate_limit_status': 'active' if self.rate_limiter else 'inactive',
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent
            }
            
            return health_data
            
        except ImportError:
            cache_stats = cache_manager.get_stats()
            
            return {
                'deployment_mode': DEPLOYMENT_MODE.value,
                'cache_stats': cache_stats,
                'psutil_not_available': True,
                'claude_api_configured': bool(self.claude_api_key),
                'drive_service_configured': bool(self.drive_service),
                'rate_limit_status': 'active' if self.rate_limiter else 'inactive'
            }
    
    def _validate_donor_data(self, donor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean donor data with defaults"""
        required_fields = {
            'contact_person': 'there',
            'organization_name': 'your organization', 
            'sector_tags': 'education',
            'geography': 'Bihar',
            'alignment_score': '7',
            'priority': 'Medium',
            'estimated_grant_size': '₹5,00,000',
            'current_stage': 'Unknown',
            'notes': 'No additional context'
        }
        
        validated_data = {}
        for field, default in required_fields.items():
            value = donor_data.get(field, default)
            # Sanitize input to prevent injection
            if isinstance(value, str):
                if SECURITY_CONFIG['sanitize_inputs']:
                    value = self._sanitize_input(value)
                value = value[:SECURITY_CONFIG['max_input_length']] if len(value) > SECURITY_CONFIG['max_input_length'] else value
            validated_data[field] = value
        
        return validated_data
    
    def _sanitize_input(self, text: str) -> str:
        """Sanitize input to prevent injection attacks"""
        if not isinstance(text, str):
            return str(text)
        
        # Remove potentially dangerous characters
        text = re.sub(r'[<>"\'\{\}]', '', text)
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def set_drive_service(self, drive_service):
        """Set Google Drive service for reading donor profiles"""
        self.drive_service = drive_service
        logger.info("Google Drive service configured for donor profiles")
    
    def set_mode(self, mode: str) -> str:
        """Set the email generation mode"""
        if mode in ["claude", "template"]:
            self.enhancement_mode = mode
            logger.info(f"Email generation mode set to: {mode}")
            return f"Email generation mode set to: {mode}"
        else:
            return f"Invalid mode '{mode}'. Use 'claude' or 'template'."
    
    def get_mode(self) -> str:
        """Get current email generation mode"""
        return self.enhancement_mode
    
    def get_available_templates(self) -> Dict[str, str]:
        """Get available email templates - combines Drive templates with hardcoded fallbacks"""
        try:
            # First, try to get templates from Drive
            drive_templates = self._get_templates_from_drive()
            
            # If Drive templates found, use them
            if drive_templates:
                logger.info(f"Found {len(drive_templates)} templates from Drive")
                return drive_templates
            
            # Fallback to hardcoded templates if Drive is not available
            logger.info("Using hardcoded template fallbacks")
            return self._get_hardcoded_templates()
            
        except Exception as e:
            logger.error(f"Error getting templates: {e}, using hardcoded fallbacks")
            return self._get_hardcoded_templates()
    
    def _get_hardcoded_templates(self) -> Dict[str, str]:
        """Get hardcoded template definitions as fallback"""
        return {
            # Stage 1: Prospecting / Outreach
            "identification": "Initial outreach and introduction",
            "intro": "First introduction to a new donor",
            "concept": "Concise concept pitch (2-3 paragraphs)",
            "followup": "Follow-up messages",
            
            # Stage 2: Engagement
            "engagement": "Relationship building and deeper discussion",
            "meeting_request": "Request a donor meeting/call",
            "thanks_meeting": "Thank-you mail after initial meeting",
            "connect": "Warm connection email (referral/introduction)",
            
            # Stage 3: Proposal Submission
            "proposal": "Formal proposal submission",
            "proposal_cover": "Cover note for sending a proposal",
            "proposal_reminder": "Reminder for pending proposal response",
            "pitch": "Strong pitch highlighting alignment & value",
            
            # Stage 4: Stewardship for Fundraising
            "celebration": "Grant secured celebrations",
            "impact_story": "Share story to inspire interest",
            "invite": "Invite donor to events",
            "festival_greeting": "Donor-friendly relationship building"
        }
    
    def _get_templates_from_drive(self) -> Dict[str, str]:
        """Read actual template content from Drive Templates folder"""
        if not self.drive_service:
            logger.warning("Google Drive service not configured, skipping Drive templates")
            return {}
        
        try:
            # Search for Templates folder in root or common locations
            templates_folder = self._find_templates_folder()
            if not templates_folder:
                logger.info("Templates folder not found in Drive")
                return {}
            
            # Get template files from the folder
            template_files = self._get_template_files_from_folder(templates_folder['id'])
            
            # Extract and process template content
            templates = {}
            for file_info in template_files:
                template_name = self._extract_template_name(file_info['name'])
                template_content = self._extract_template_content(file_info)
                
                if template_content:
                    templates[template_name] = template_content
                    logger.info(f"Loaded template: {template_name} from {file_info['name']}")
            
            return templates
            
        except Exception as e:
            logger.error(f"Error reading templates from Drive: {e}")
            return {}
    
    def _find_templates_folder(self) -> Optional[Dict[str, Any]]:
        """Find the Templates folder in Google Drive"""
        try:
            # Common folder names for templates
            possible_names = [
                "Templates",
                "Email Templates", 
                "Email_Templates",
                "Templates/Email_Templates",
                "Fundraising Templates"
            ]
            
            for folder_name in possible_names:
                query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
                results = self.drive_service.files().list(
                    q=query,
                    spaces='drive',
                    fields='files(id, name, parents)'
                ).execute()
                
                if results.get('files'):
                    folder = results['files'][0]
                    logger.info(f"Found templates folder: {folder['name']} (ID: {folder['id']})")
                    return folder
            
            # If not found in root, search in subfolders
            query = "mimeType='application/vnd.google-apps.folder' and name contains 'Template' and trashed=false"
            results = self.drive_service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, parents)'
            ).execute()
            
            if results.get('files'):
                folder = results['files'][0]
                logger.info(f"Found templates folder in subfolder: {folder['name']} (ID: {folder['id']})")
                return folder
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding templates folder: {e}")
            return None
    
    def _get_template_files_from_folder(self, folder_id: str) -> List[Dict[str, Any]]:
        """Get template files from a specific folder"""
        try:
            # Search for document files in the templates folder
            query = f"'{folder_id}' in parents and (mimeType contains 'document' or mimeType contains 'pdf' or mimeType contains 'text') and trashed=false"
            
            results = self.drive_service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, webViewLink, createdTime, modifiedTime)',
                orderBy='modifiedTime desc'
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"Found {len(files)} template files in folder {folder_id}")
            return files
            
        except Exception as e:
            logger.error(f"Error getting template files from folder: {e}")
            return []
    
    def _extract_template_name(self, filename: str) -> str:
        """Extract template name from filename"""
        # Remove file extensions
        name = filename.replace('.docx', '').replace('.pdf', '').replace('.txt', '')
        
        # Remove common prefixes/suffixes
        name = name.replace('Template', '').replace('Email', '').replace('_', ' ').replace('-', ' ')
        
        # Convert to lowercase key
        name = name.strip().lower()
        
        # Map common variations to standard names
        name_mapping = {
            'identification': 'identification',
            'intro': 'intro',
            'introduction': 'intro',
            'engagement': 'engagement',
            'proposal': 'proposal',
            'followup': 'followup',
            'follow up': 'followup',
            'follow-up': 'followup',
            'meeting request': 'meeting_request',
            'meeting_request': 'meeting_request',
            'celebration': 'celebration',
            'impact story': 'impact_story',
            'impact_story': 'impact_story'
        }
        
        return name_mapping.get(name, name)
    
    def _extract_template_content(self, file_info: Dict[str, Any]) -> Optional[str]:
        """Extract content from template file"""
        try:
            file_id = file_info['id']
            mime_type = file_info['mimeType']
            
            if mime_type == 'application/vnd.google-apps.document':
                # Google Docs - export as plain text
                response = self.drive_service.files().export_media(
                    fileId=file_id,
                    mimeType='text/plain'
                ).execute()
                return response.decode('utf-8')
                
            elif mime_type == 'application/pdf':
                # PDF - export as plain text (basic extraction)
                response = self.drive_service.files().export_media(
                    fileId=file_id,
                    mimeType='text/plain'
                ).execute()
                return response.decode('utf-8')
                
            elif mime_type == 'text/plain':
                # Plain text file
                response = self.drive_service.files().get_media(fileId=file_id).execute()
                return response.decode('utf-8')
                
            else:
                logger.warning(f"Unsupported file type for template: {mime_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting content from template file {file_info.get('name', 'unknown')}: {e}")
            return None
    
    def get_template_content(self, template_name: str) -> Optional[str]:
        """Get the actual content of a specific template"""
        try:
            # First check if we have the template content loaded
            templates = self.get_available_templates()
            
            # If templates is a dict of content (from Drive), return the content
            if isinstance(templates.get(template_name), str) and len(templates[template_name]) > 50:
                # This looks like actual content, not just a description
                return templates[template_name]
            
            # If not, try to get from Drive directly
            if self.drive_service:
                drive_templates = self._get_templates_from_drive()
                return drive_templates.get(template_name)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting template content for {template_name}: {e}")
            return None
    
    def generate_email(self, template_type: str, donor_data: Dict[str, Any], mode: Optional[str] = None) -> Tuple[str, str]:
        """Generate email based on template type and donor data"""
        try:
            # Validate and sanitize donor data
            validated_data = self._validate_donor_data(donor_data)
            
            # Use specified mode or fall back to default
            generation_mode = mode or self.enhancement_mode
            
            if generation_mode == "claude":
                return self._generate_with_claude(template_type, validated_data)
            else:
                return self._generate_custom_email(template_type, validated_data)
                
        except Exception as e:
            logger.error(f"Email generation failed: {e}")
            return "", f"Email generation failed: {str(e)}"
    
    def _get_donor_profile_from_drive(self, organization_name: str) -> Optional[Dict[str, Any]]:
        """Read donor profile from Google Drive based on organization name"""
        if not self.drive_service:
            logger.warning("Google Drive service not configured, skipping donor profile")
            return None
        
        # Generate cache key for this organization
        cache_key = cache_manager.get_cache_key("donor_profile", organization_name)
        
        # Check global cache first
        try:
            cached_profile = cache_manager.get(cache_key)
            if cached_profile:
                logger.info(f"Using cached donor profile for {organization_name}")
                return cached_profile
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
        
        try:
            # Escape single quotes in organization name for query
            safe_org_name = organization_name.replace("'", "\\'")
            query = f"name contains '{safe_org_name}' and (mimeType contains 'application/pdf' or mimeType contains 'application/vnd.google-apps.document')"
            
            # Add timeout and retry logic for API call
            try:
                results = self.drive_service.files().list(
                    q=query,
                    spaces='drive',
                    fields='files(id, name, mimeType, webViewLink, createdTime, modifiedTime)',
                    orderBy='modifiedTime desc'
                ).execute()
            except Exception as api_error:
                logger.error(f"Google Drive API error: {api_error}")
                return None
            
            files = results.get('files', [])
            
            if not files:
                logger.info(f"No donor profile found for {organization_name}")
                return None
            
            # Get the most recent profile
            profile_file = files[0]
            logger.info(f"Found donor profile: {profile_file['name']} for {organization_name}")
            
            # Extract profile content based on file type
            profile_content = self._extract_profile_content(profile_file)
            
            # Create profile data
            profile_data = {
                'file_id': profile_file['id'],
                'file_name': profile_file['name'],
                'file_type': profile_file['mimeType'],
                'web_link': profile_file.get('webViewLink'),
                'created': profile_file.get('createdTime'),
                'modified': profile_file.get('modifiedTime'),
                'content': profile_content,
                'content_summary': self._summarize_profile_content(profile_content)
            }
            
            # Cache in global cache with error handling
            try:
                cache_manager.set(cache_key, profile_data, CACHE_CONFIG['profile_timeout'])
            except Exception as e:
                logger.warning(f"Cache storage failed: {e}")
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Error reading donor profile from Drive: {e}")
            return None
    
    def _extract_profile_content(self, profile_file: Dict[str, Any]) -> str:
        """Extract content from donor profile file"""
        try:
            file_id = profile_file['id']
            mime_type = profile_file['mimeType']
            
            if 'application/pdf' in mime_type:
                # For PDFs, we'll get metadata and try to extract text
                # Note: Full PDF text extraction requires additional libraries
                return f"PDF Profile: {profile_file['name']} - Content extraction limited"
                
            elif 'application/vnd.google-apps.document' in mime_type:
                # For Google Docs, we can export as text
                try:
                    response = self.drive_service.files().export_media(
                        fileId=file_id,
                        mimeType='text/plain'
                    ).execute()
                    
                    if response:
                        return response.decode('utf-8')
                    else:
                        return f"Google Doc Profile: {profile_file['name']} - Content export failed"
                        
                except Exception as e:
                    logger.warning(f"Could not export Google Doc content: {e}")
                    return f"Google Doc Profile: {profile_file['name']} - Content export failed"
            
            else:
                return f"Profile File: {profile_file['name']} - Unsupported format"
                
        except Exception as e:
            logger.error(f"Error extracting profile content: {e}")
            return f"Profile content extraction failed: {e}"
    
    def _summarize_profile_content(self, content: str) -> str:
        """Create a summary of profile content for Claude context"""
        if not content or len(content) < 50:
            return "No detailed profile content available"
        
        # Create a smart summary (first 200 chars + key points)
        summary = content[:200] + "...\n\n"
        
        # Extract key information patterns
        key_patterns = [
            'mission', 'vision', 'values', 'focus', 'priorities',
            'programs', 'initiatives', 'partnerships', 'impact',
            'geographic', 'sector', 'target', 'beneficiaries'
        ]
        
        found_key_points = []
        content_lower = content.lower()
        
        for pattern in key_patterns:
            if pattern in content_lower:
                # Find the sentence containing this pattern
                sentences = content.split('.')
                for sentence in sentences:
                    if pattern in sentence.lower() and len(sentence.strip()) > 20:
                        found_key_points.append(sentence.strip())
                        break
        
        if found_key_points:
            summary += "Key Profile Points:\n"
            for point in found_key_points[:5]:  # Limit to 5 key points
                summary += f"• {point}\n"
        
        return summary
    
    def _build_claude_context(self, template_type: str, donor_data: Dict[str, Any], base_subject: str, base_body: str) -> str:
        """Build comprehensive context for Claude enhancement including Drive profile data"""
        
        # Get donor profile from Google Drive
        donor_profile = self._get_donor_profile_from_drive(donor_data.get('organization_name', ''))
        
        context = f"""
        You are a fundraising expert at Diksha Foundation. Your task is to ENHANCE an existing email template by making it more personalized, engaging, and professional.
        
        ORGANIZATION CONTEXT (from Google Sheets):
        - Name: {donor_data.get('organization_name', 'Unknown')}
        - Contact Person: {donor_data.get('contact_person', 'Unknown')}
        - Sector: {donor_data.get('sector_tags', 'Education')}
        - Geography: {donor_data.get('geography', 'India')}
        - Alignment Score: {donor_data.get('alignment_score', '7')}/10
        - Priority: {donor_data.get('priority', 'Medium')}
        - Current Stage: {donor_data.get('current_stage', 'Unknown')}
        - Estimated Grant Size: {donor_data.get('estimated_grant_size', '₹5,00,000')}
        - Notes: {donor_data.get('notes', 'No additional context')}
        """
        
        # Add Google Drive profile context if available
        if donor_profile:
            context += f"""
        
        DONOR PROFILE (from Google Drive):
        - Profile File: {donor_profile['file_name']}
        - File Type: {donor_profile['file_type']}
        - Last Modified: {donor_profile['modified']}
        - Profile Summary: {donor_profile['content_summary']}
        
        Use this profile information to make the email more personalized and relevant to their specific mission and programs.
        """
        else:
            context += """
        
        DONOR PROFILE: No detailed profile found in Google Drive
        Use the available Google Sheets data for personalization.
        """
        
        context += f"""
        
        DIKSHA FOUNDATION ACHIEVEMENTS:
        - {DIKSHA_INFO['youth_trained']} youth trained in digital literacy
        - {DIKSHA_INFO['employment_rate']} employment rate post-training
        - Focus on underserved communities in {DIKSHA_INFO['location']}
        - Proven track record since {DIKSHA_INFO['founding_year']}
        - Programs: {', '.join(DIKSHA_INFO['programs'])}
        
        TEMPLATE TYPE: {template_type.title()}
        
        BASE TEMPLATE TO ENHANCE:
        SUBJECT: {base_subject}
        BODY: {base_body}
        
        ENHANCEMENT REQUIREMENTS:
        1. Keep the core structure and key points from the base template
        2. Make the language more engaging and professional
        3. Add specific references to the organization's sector and geography
        4. Include relevant Diksha achievements that align with their interests
        5. Personalize the tone based on their alignment score and priority
        6. Add more compelling subject lines if possible
        7. Maintain the same length (within 20% of original)
        8. Keep the professional signature format
        9. Use donor profile information to make content more relevant and personalized
        10. Reference specific programs or initiatives mentioned in their profile
        
        STAGE-SPECIFIC ENHANCEMENTS:
        """
        
        # Stage-specific enhancement instructions
        stage_enhancements = {
            "identification": "Make the introduction more compelling, highlight specific sector alignment, and create urgency for initial contact. Use profile information to show you've researched their organization.",
            "engagement": "Deepen the relationship building, reference previous interactions, and make the next steps more specific. Use profile insights to show deeper understanding.",
            "proposal": "Enhance the proposal presentation, make budget details more compelling, and strengthen the call to action. Align with their profile priorities and programs.",
            "followup": "Make the follow-up more engaging, reference specific previous points, and create clear next steps. Use profile context to personalize follow-up.",
            "celebration": "Make the celebration more heartfelt, emphasize partnership value, and outline clear next steps. Reference profile information to show partnership alignment."
        }
        
        context += f"{stage_enhancements.get(template_type, 'Enhance professionalism and engagement while maintaining core message.')}"
        
        context += f"\n\nPlease enhance the base template above. Return the enhanced version in this exact format:\n\nSUBJECT: [enhanced subject line]\n\nBODY:\n[enhanced email body]\n\nSIGNATURE:\n[professional signature]"
        
        return context
    
    @retry_on_failure(max_retries=3)
    def _generate_with_claude(self, template_type: str, donor_data: Dict[str, Any]) -> Tuple[str, str]:
        """Generate enhanced email using Claude API with template as base and Drive profile data"""
        try:
            import anthropic
            
            if not self.claude_api_key:
                logger.warning("Claude API key not found, falling back to template system")
                return self._generate_custom_email(template_type, donor_data)
            
            client = anthropic.Anthropic(api_key=self.claude_api_key)
            
            # Try to get actual template content from Drive first
            drive_template_content = self.get_template_content(template_type)
            
            if drive_template_content:
                logger.info(f"Using Drive template content for {template_type}")
                # Use Drive template as base
                base_subject, base_body = self._generate_from_drive_template(template_type, donor_data, drive_template_content)
            else:
                logger.info(f"No Drive template found for {template_type}, using hardcoded template")
                # Fallback to hardcoded template
                base_subject, base_body = self._generate_custom_email(template_type, donor_data)
            
            if not base_subject or not base_body:
                logger.warning("Base template generation failed, falling back to template system")
                return self._generate_custom_email(template_type, donor_data)
            
            # Create comprehensive context for Claude to enhance the template
            context = self._build_claude_context(template_type, donor_data, base_subject, base_body)
            
            # Generate enhanced email using Claude
            message = client.messages.create(
                model="claude-sonnet-4-20250514",  # Updated from deprecated model
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": context
                    }
                ]
            )
            
            # Parse Claude's response
            subject, body, signature = self._parse_claude_response(message.content[0].text)
            
            # Validate enhancement quality
            if not subject or not body:
                logger.warning("Claude enhancement parsing failed, using base template")
                return base_subject, base_body
            
            # Check if enhancement is significantly different from base
            similarity = self._calculate_similarity(
                f"{base_subject} {base_body}".lower(),
                f"{subject} {body}".lower()
            )
            
            # Simple similarity check - if too similar, enhance manually
            if similarity > self.similarity_threshold:
                logger.info("Claude enhancement too similar to base, applying manual enhancements")
                subject, body = self._apply_manual_enhancements(base_subject, base_body, donor_data, template_type)
            else:
                logger.info("Claude enhancement successful, using AI-enhanced version")
            
            return subject, body + "\n\n" + signature
            
        except ImportError:
            logger.warning("Anthropic package not installed, falling back to template system")
            return self._generate_custom_email(template_type, donor_data)
        except Exception as e:
            logger.error(f"Claude API error: {e}, falling back to template system")
            return self._generate_custom_email(template_type, donor_data)
    
    def _generate_from_drive_template(self, template_type: str, donor_data: Dict[str, Any], template_content: str) -> Tuple[str, str]:
        """Generate email using actual template content from Drive"""
        try:
            # Parse the template content to extract subject and body
            subject, body = self._parse_drive_template_content(template_content)
            
            if not subject or not body:
                logger.warning(f"Failed to parse Drive template content for {template_type}")
                return "", f"Template parsing failed for {template_type}"
            
            # Customize the template with donor data
            customized_subject = self._customize_subject(subject, donor_data)
            customized_body = self._customize_body(body, donor_data)
            
            logger.info(f"Successfully generated email from Drive template: {template_type}")
            return customized_subject, customized_body
            
        except Exception as e:
            logger.error(f"Error generating from Drive template {template_type}: {e}")
            return "", f"Drive template generation failed: {str(e)}"
    
    def _parse_drive_template_content(self, template_content: str) -> Tuple[str, str]:
        """Parse Drive template content to extract subject and body"""
        try:
            lines = template_content.split('\n')
            subject = ""
            body = ""
            
            current_section = None
            for line in lines:
                line = line.strip()
                
                # Look for subject indicators
                if any(keyword in line.lower() for keyword in ['subject:', 'title:', 'email subject:']):
                    subject = line.split(':', 1)[1].strip() if ':' in line else line
                    current_section = "body"
                    continue
                
                # Look for body section indicators
                if any(keyword in line.lower() for keyword in ['body:', 'content:', 'message:', 'email body:']):
                    current_section = "body"
                    continue
                
                # If we have a subject and we're in body section, add to body
                if current_section == "body" and line:
                    body += line + "\n"
                
                # If we don't have a subject yet and line looks like a subject, use it
                elif not subject and line and len(line) < 100 and not line.startswith('Dear'):
                    subject = line
            
            # If no subject found, generate a default one
            if not subject:
                subject = "Partnership Opportunity - Diksha Foundation"
            
            # If no body found, use the entire content as body
            if not body:
                body = template_content
            
            return subject, body.strip()
            
        except Exception as e:
            logger.error(f"Error parsing Drive template content: {e}")
            return "Partnership Opportunity", template_content
    
    def _parse_claude_response(self, response_text: str) -> Tuple[str, str, str]:
        """Parse Claude's response to extract subject, body, and signature"""
        if not response_text:
            logger.warning("Empty Claude response received")
            return "", "", ""
        
        lines = response_text.split('\n')
        subject = ""
        body = ""
        signature = ""
        
        current_section = None
        for line in lines:
            line = line.strip()
            if line.startswith("SUBJECT:"):
                subject = line.replace("SUBJECT:", "").strip()
                current_section = "subject"
            elif line.startswith("BODY:"):
                current_section = "body"
            elif line.startswith("SIGNATURE:"):
                current_section = "signature"
            elif current_section == "body" and line:
                body += line + "\n"
            elif current_section == "signature" and line:
                signature += line + "\n"
        
        # Validate that we got at least subject and body
        if not subject or not body:
            logger.warning(f"Claude response parsing incomplete. Subject: '{subject[:50]}...', Body: '{body[:50]}...'")
        
        return subject.strip(), body.strip(), signature.strip()
    
    def get_donor_profile_info(self, organization_name: str) -> Dict[str, Any]:
        """Get donor profile information for debugging and testing"""
        try:
            profile = self._get_donor_profile_from_drive(organization_name)
            
            if profile:
                return {
                    "ok": True,
                    "organization": organization_name,
                    "profile_found": True,
                    "file_info": {
                        "name": profile['file_name'],
                        "type": profile['file_type'],
                        "modified": profile['modified'],
                        "web_link": profile['web_link']
                    },
                    "content_summary": profile['content_summary'],
                    "content_length": len(profile['content']) if profile['content'] else 0,
                    "drive_service": "configured" if self.drive_service else "not configured"
                }
            else:
                return {
                    "ok": True,
                    "organization": organization_name,
                    "profile_found": False,
                    "message": "No donor profile found in Google Drive",
                    "drive_service": "configured" if self.drive_service else "not configured"
                }
                
        except Exception as e:
            logger.error(f"Error getting donor profile info: {e}")
            return {
                "ok": False,
                "organization": organization_name,
                "error": str(e),
                "drive_service": "configured" if self.drive_service else "not configured"
            }
    
    def _generate_custom_email(self, template_type: str, donor_data: Dict[str, Any]) -> Tuple[str, str]:
        """Generate custom email based on template and donor data (fallback system)"""
        try:
            # Get base template
            base_template = self._get_base_template(template_type)
            if not base_template:
                return "", f"Template type '{template_type}' not found. Available: {', '.join(self.get_available_templates().keys())}"
            
            # Customize template with donor data
            subject = self._customize_subject(base_template['subject'], donor_data)
            body = self._customize_body(base_template['body'], donor_data)
            
            return subject, body
            
        except Exception as e:
            logger.error(f"Template generation failed: {e}")
            return "", f"Template generation failed: {e}"
    
    def _get_base_template(self, template_type: str) -> Optional[Dict[str, str]]:
        """Get base template for the specified type"""
        templates = {
                         "identification": {
                 "subject": "Partnership Opportunity with Diksha Foundation - Digital Skills Training",
                 "body": """Dear {{contact_person}},
 
 I hope this message finds you well. I'm reaching out from Diksha Foundation, where we've been transforming lives through digital skills training and youth empowerment in Bihar since 2010.
 
 Given {{organization_name}}'s focus on {{sector_tags}}, I believe there is strong alignment between our mission and your organization's goals. We've successfully trained over 2,500 youth in digital literacy, with an 85% employment rate post-training.
 
 Our programs focus on:
 • Digital Skills Training for underserved communities
 • Youth Empowerment through technology education
 • Rural Education Access in Bihar
 
 I would love to discuss how we might collaborate to expand our impact. Would you be available for a brief call next week to explore potential partnership opportunities?
 
 Looking forward to connecting.
 
 Best regards,
 Team Diksha Foundation"""
             },
                         "intro": {
                 "subject": "First Introduction to Diksha Foundation - Digital Skills Training",
                 "body": """Dear {{contact_person}},
 
 I hope this message finds you well. I'm {{contact_person}} from Diksha Foundation, and I wanted to introduce myself and our work.
 
 Diksha Foundation is a non-profit organization dedicated to empowering youth through digital literacy and technology education. We've been successfully training youth in Bihar for over 10 years, with a proven track record of 85% employment post-training.
 
 Our programs include:
 • Digital Literacy Training for underserved communities
 • Youth Empowerment through technology education
 • Rural Education Access in Bihar
 
 I'd love to learn more about {{organization_name}}'s mission and how we might collaborate to create meaningful impact.
 
 Looking forward to connecting.
 
 Best regards,
 {{contact_person}} from Diksha Foundation"""
             },
            "concept": {
                "subject": "A Concise Concept Pitch for Diksha Foundation",
                "body": """Dear {{contact_person}},

I hope this message finds you well. I'm {{contact_person}} from Diksha Foundation, and I wanted to share a concise concept pitch for our work.

Diksha Foundation is a non-profit organization that has been transforming lives through digital literacy and youth empowerment in Bihar since 2010. We've successfully trained over 2,500 youth in digital literacy, with an 85% employment rate post-training.

Our programs include:
• Digital Literacy Training for underserved communities
• Youth Empowerment through technology education
• Rural Education Access in Bihar

We believe in creating sustainable impact and are looking for strategic partnerships to expand our reach.

Would you be interested in a brief call to discuss how we might collaborate?

Looking forward to connecting.

Best regards,
{{contact_person}} from Diksha Foundation"""
            },
            "engagement": {
                "subject": "Deepening Our Partnership Discussion - Diksha Foundation",
                "body": """Dear {{contact_person}},

Thank you for your initial interest in our work at Diksha Foundation. I'm excited to explore how we can deepen our potential partnership.

Based on our previous discussion and {{organization_name}}'s expertise in {{sector_tags}}, I see excellent opportunities for collaboration. Our proven track record in Bihar demonstrates the scalability of our model, and I believe we could achieve even greater impact together.

Key areas for discussion:
• Program expansion opportunities
• Resource sharing and capacity building
• Impact measurement and reporting
• Long-term partnership framework

Given your estimated grant size of {{estimated_grant_size}}, we could significantly scale our operations and reach more underserved communities.

Would you be available for a detailed discussion next week? I can prepare a comprehensive proposal based on your specific interests and requirements.

Best regards,
Team Diksha Foundation"""
            },
            "meeting_request": {
                "subject": "Request for a Meeting/Call with Diksha Foundation",
                "body": """Dear {{contact_person}},

I hope this message finds you well. I'm {{contact_person}} from Diksha Foundation, and I'd like to request a meeting or call to discuss potential collaboration.

Based on our previous discussions and {{organization_name}}'s focus on {{sector_tags}}, I believe we have a strong alignment. I'd like to explore how we can work together to create meaningful impact.

Would you be available for a meeting or call at your earliest convenience? I can prepare a detailed proposal and answer any questions you might have.

Looking forward to connecting.

Best regards,
{{contact_person}} from Diksha Foundation"""
            },
            "thanks_meeting": {
                "subject": "Thank You for Our Recent Meeting - Diksha Foundation",
                "body": """Dear {{contact_person}},

Thank you for the opportunity to discuss potential collaboration between {{organization_name}} and Diksha Foundation.

I'm excited about the alignment between our missions and the potential for partnership. I'd like to explore how we can work together to create meaningful impact.

Would you be available for a follow-up call to discuss specific partnership details and next steps?

Looking forward to connecting.

Best regards,
{{contact_person}} from Diksha Foundation"""
            },
            "connect": {
                "subject": "Warm Connection Email - Diksha Foundation",
                "body": """Dear {{contact_person}},

I hope this message finds you well. I'm {{contact_person}} from Diksha Foundation, and I wanted to reach out as a warm connection.

I've heard about {{organization_name}}'s excellent work in {{sector_tags}}, and I believe there's a strong alignment between our missions. I'd love to learn more about your organization and how we might collaborate.

Would you be open to a brief call to discuss potential partnership opportunities?

Looking forward to connecting.

Best regards,
{{contact_person}} from Diksha Foundation"""
            },
            "proposal": {
                "subject": "Formal Partnership Proposal - Diksha Foundation Digital Skills Program",
                "body": """Dear {{contact_person}},

Thank you for the opportunity to submit a formal partnership proposal to {{organization_name}}. Based on our discussions and your organization's commitment to {{sector_tags}}, I'm confident this partnership will create significant impact.

PROPOSAL OVERVIEW:
Program: Digital Skills Training & Youth Empowerment
Duration: 12 months (extendable)
Target: 500+ youth in underserved communities
Location: Bihar (expandable to {{geography}}} if different)

BUDGET BREAKDOWN:
• Training Materials & Technology: 40%
• Staff & Instructors: 35%
• Community Outreach: 15%
• Monitoring & Evaluation: 10%

EXPECTED OUTCOMES:
• 500+ youth trained in digital skills
• 80%+ employment rate post-training
• Measurable impact on community development
• Scalable model for other regions

NEXT STEPS:
1. Proposal review meeting
2. Budget discussion and approval
3. Partnership agreement finalization
4. Program launch and implementation

I'm available for a detailed presentation at your convenience. Please let me know your preferred time and format.

Best regards,
Team Diksha Foundation"""
            },
            "proposal_cover": {
                "subject": "Cover Note for Partnership Proposal - Diksha Foundation",
                "body": """Dear {{contact_person}},

I hope this message finds you well. I'm {{contact_person}} from Diksha Foundation, and I wanted to submit a formal partnership proposal to {{organization_name}}.

Based on our discussions and your organization's commitment to {{sector_tags}}, I'm confident this partnership will create significant impact.

PROPOSAL OVERVIEW:
Program: Digital Skills Training & Youth Empowerment
Duration: 12 months (extendable)
Target: 500+ youth in underserved communities
Location: Bihar (expandable to {{geography}}} if different)

BUDGET BREAKDOWN:
• Training Materials & Technology: 40%
• Staff & Instructors: 35%
• Community Outreach: 15%
• Monitoring & Evaluation: 10%

EXPECTED OUTCOMES:
• 500+ youth trained in digital skills
• 80%+ employment rate post-training
• Measurable impact on community development
• Scalable model for other regions

NEXT STEPS:
1. Proposal review meeting
2. Budget discussion and approval
3. Partnership agreement finalization
4. Program launch and implementation

I'm available for a detailed presentation at your convenience. Please let me know your preferred time and format.

Best regards,
{{contact_person}} from Diksha Foundation"""
            },
            "proposal_reminder": {
                "subject": "Reminder for Partnership Proposal Response - Diksha Foundation",
                "body": """Dear {{contact_person}},

I hope this message finds you well. I'm {{contact_person}} from Diksha Foundation, and I wanted to remind you about our formal partnership proposal.

Based on our discussions and your organization's commitment to {{sector_tags}}, I'm confident this partnership will create significant impact.

PROPOSAL OVERVIEW:
Program: Digital Skills Training & Youth Empowerment
Duration: 12 months (extendable)
Target: 500+ youth in underserved communities
Location: Bihar (expandable to {{geography}}} if different)

BUDGET BREAKDOWN:
• Training Materials & Technology: 40%
• Staff & Instructors: 35%
• Community Outreach: 15%
• Monitoring & Evaluation: 10%

EXPECTED OUTCOMES:
• 500+ youth trained in digital skills
• 80%+ employment rate post-training
• Measurable impact on community development
• Scalable model for other regions

NEXT STEPS:
1. Proposal review meeting
2. Budget discussion and approval
3. Partnership agreement finalization
4. Program launch and implementation

I'm available for a detailed presentation at your convenience. Please let me know your preferred time and format.

Best regards,
{{contact_person}} from Diksha Foundation"""
            },
            "pitch": {
                "subject": "Strong Pitch Highlighting Alignment & Value - Diksha Foundation",
                "body": """Dear {{contact_person}},

I hope this message finds you well. I'm {{contact_person}} from Diksha Foundation, and I wanted to share a strong pitch highlighting our alignment and value.

Diksha Foundation is a non-profit organization that has been transforming lives through digital literacy and youth empowerment in Bihar since 2010. We've successfully trained over 2,500 youth in digital literacy, with an 85% employment rate post-training.

Our programs include:
• Digital Literacy Training for underserved communities
• Youth Empowerment through technology education
• Rural Education Access in Bihar

We believe in creating sustainable impact and are looking for strategic partnerships to expand our reach.

Would you be interested in a detailed discussion to explore how we might collaborate?

Looking forward to connecting.

Best regards,
{{contact_person}} from Diksha Foundation"""
            },
            "celebration": {
                "subject": "Celebrating Our Partnership - Diksha Foundation",
                "body": """Dear {{contact_person}},

I'm thrilled to officially welcome {{organization_name}} as a partner of Diksha Foundation! This is a momentous occasion that will enable us to create even greater impact in our communities.

Your commitment to {{sector_tags}} and our shared vision for youth empowerment makes this partnership particularly meaningful. Together, we'll be able to:

• Expand our digital skills training programs
• Reach more underserved communities
• Create sustainable employment opportunities
• Build a stronger foundation for future growth

NEXT STEPS:
1. Partnership agreement signing
2. Program planning and team coordination
3. Community outreach and participant recruitment
4. Regular progress updates and collaboration

I'm excited to work together and look forward to celebrating our shared successes. Thank you for believing in our mission and joining us on this journey.

Here's to making a difference together!

Best regards,
Team Diksha Foundation"""
            },
            "impact_story": {
                "subject": "Impact Story - Diksha Foundation",
                "body": """Dear {{contact_person}},

I hope this message finds you well. I'm {{contact_person}} from Diksha Foundation, and I wanted to share a story about our impact.

Diksha Foundation has been transforming lives through digital literacy and youth empowerment in Bihar since 2010. We've successfully trained over 2,500 youth in digital literacy, with an 85% employment rate post-training.

Our programs include:
• Digital Literacy Training for underserved communities
• Youth Empowerment through technology education
• Rural Education Access in Bihar

We believe in creating sustainable impact and are looking for strategic partnerships to expand our reach.

Would you be interested in a detailed discussion to learn more about our impact and how we might collaborate?

Looking forward to connecting.

Best regards,
{{contact_person}} from Diksha Foundation"""
            },
            "invite": {
                "subject": "Invite to Diksha Foundation Events - Digital Skills Training",
                "body": """Dear {{contact_person}},

I hope this message finds you well. I'm {{contact_person}} from Diksha Foundation, and I wanted to invite you to our upcoming digital skills training events.

Diksha Foundation is a non-profit organization that has been transforming lives through digital literacy and youth empowerment in Bihar since 2010. We've successfully trained over 2,500 youth in digital literacy, with an 85% employment rate post-training.

Our programs include:
• Digital Literacy Training for underserved communities
• Youth Empowerment through technology education
• Rural Education Access in Bihar

We believe in creating sustainable impact and are looking for strategic partnerships to expand our reach.

Would you be interested in attending one of our upcoming events?

Looking forward to connecting.

Best regards,
{{contact_person}} from Diksha Foundation"""
            },
            "festival_greeting": {
                "subject": "Festival Greeting - Diksha Foundation",
                "body": """Dear {{contact_person}},

I hope this message finds you well. I'm {{contact_person}} from Diksha Foundation, and I wanted to send you a festive greeting.

Diksha Foundation is a non-profit organization that has been transforming lives through digital literacy and youth empowerment in Bihar since 2010. We've successfully trained over 2,500 youth in digital literacy, with an 85% employment rate post-training.

Our programs include:
• Digital Literacy Training for underserved communities
• Youth Empowerment through technology education
• Rural Education Access in Bihar

We believe in creating sustainable impact and are looking for strategic partnerships to expand our reach.

Would you like to celebrate this festive season together?

Looking forward to connecting.

Best regards,
{{contact_person}} from Diksha Foundation"""
            }
        }
        
        return templates.get(template_type.lower())
    
    def _customize_subject(self, subject: str, donor_data: Dict[str, Any]) -> str:
        """Customize email subject with donor data"""
        customized = subject
        
        # Fix: Use single braces for replacement - more robust
        customized = customized.replace("{{contact_person}}", donor_data.get('contact_person', 'there'))
        customized = customized.replace("{{organization_name}}", donor_data.get('organization_name', 'your organization'))
        customized = customized.replace("{{sector_tags}}", donor_data.get('sector_tags', 'education and technology'))
        customized = customized.replace("{{geography}}", donor_data.get('geography', 'Bihar'))
        customized = customized.replace("{{estimated_grant_size}}", donor_data.get('estimated_grant_size', '₹5,00,000'))
        
        return customized
    
    def _customize_body(self, body: str, donor_data: Dict[str, Any]) -> str:
        """Customize email body with donor data"""
        customized = body
        
        # Fix: Use single braces for replacement - more robust
        customized = customized.replace("{{contact_person}}", donor_data.get('contact_person', 'there'))
        customized = customized.replace("{{organization_name}}", donor_data.get('organization_name', 'your organization'))
        customized = customized.replace("{{sector_tags}}", donor_data.get('sector_tags', 'education and technology'))
        customized = customized.replace("{{geography}}", donor_data.get('geography', 'Bihar'))
        customized = customized.replace("{{estimated_grant_size}}", donor_data.get('estimated_grant_size', '₹5,00,000'))
        
        return customized
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity for enhancement validation"""
        try:
            from difflib import SequenceMatcher
            return SequenceMatcher(None, text1, text2).ratio()
        except ImportError:
            # Fallback similarity calculation
            words1 = set(text1.split())
            words2 = set(text2.split())
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            return len(intersection) / len(union) if union else 0
    
    def _apply_manual_enhancements(self, base_subject: str, base_body: str, donor_data: Dict[str, Any], template_type: str) -> Tuple[str, str]:
        """Apply manual enhancements when Claude enhancement is insufficient"""
        try:
            # Enhance subject line
            enhanced_subject = base_subject
            if donor_data.get('priority') == 'High':
                enhanced_subject = enhanced_subject.replace('Partnership', 'Priority Partnership')
            try:
                alignment_score = int(donor_data.get('alignment_score', 7))
            except (ValueError, TypeError):
                alignment_score = 7
            
            if alignment_score >= 8:
                enhanced_subject = enhanced_subject.replace('Opportunity', 'High-Alignment Opportunity')
            
            # Enhance body with specific details
            enhanced_body = base_body
            
            # Add sector-specific enhancements
            sector = donor_data.get('sector_tags', '').lower()
            if 'technology' in sector or 'digital' in sector:
                enhanced_body = enhanced_body.replace(
                    'digital skills and education',
                    f'digital skills and education, particularly relevant to {donor_data.get("organization_name", "your organization")}\'s focus on {sector}'
                )
            
            # Add geography-specific enhancements
            geography = donor_data.get('geography', '')
            if geography and geography != 'India':
                enhanced_body = enhanced_body.replace(
                    'in Bihar',
                    f'in {geography}, with our proven success in Bihar as a scalable model'
                )
            
            # Add alignment score enhancements
            if alignment_score >= 8:
                enhanced_body = enhanced_body.replace(
                    'I believe there is strong alignment',
                    f'I believe there is exceptional alignment (score: {alignment_score}/10)'
                )
            
            return enhanced_subject, enhanced_body
            
        except Exception as e:
            logger.error(f"Manual enhancement failed: {e}")
            return base_subject, base_body
    
    def compare_templates(self, template_type: str, donor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare base template vs. enhanced version"""
        try:
            # Generate base template
            base_subject, base_body = self._generate_custom_email(template_type, donor_data)
            
            # Generate enhanced version
            enhanced_subject, enhanced_body = self._generate_with_claude(template_type, donor_data)
            
            # Calculate similarity
            base_text = f"{base_subject} {base_body}".lower()
            enhanced_text = f"{enhanced_subject} {enhanced_body}".lower()
            similarity = self._calculate_similarity(base_text, enhanced_text)
            
            return {
                "ok": True,
                "comparison": {
                    "base_template": {
                        "subject": base_subject,
                        "body": base_body,
                        "total_length": len(f"{base_subject} {base_body}")
                    },
                    "enhanced_template": {
                        "subject": enhanced_subject,
                        "body": enhanced_body,
                        "total_length": len(f"{enhanced_subject} {enhanced_body}")
                    },
                    "enhancement_metrics": {
                        "similarity_score": round(similarity, 3),
                        "improvement_percentage": round((1 - similarity) * 100, 1),
                        "length_change": len(f"{enhanced_subject} {enhanced_body}") - len(f"{base_subject} {base_body}")
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Template comparison failed: {e}")
            return {
                "ok": False,
                "error": f"Template comparison failed: {e}"
            }
