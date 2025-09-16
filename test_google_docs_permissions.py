#!/usr/bin/env python3
"""
Test Google Docs service account permissions
"""

import os
import json
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_google_docs_permissions():
    """Test if the service account can create documents in the specified folder"""

    try:
        # Get credentials from environment
        creds_base64 = os.getenv('GOOGLE_CREDENTIALS_BASE64')
        if not creds_base64:
            logger.error("❌ GOOGLE_CREDENTIALS_BASE64 environment variable not found")
            return False

        # Decode credentials
        creds_json = base64.b64decode(creds_base64).decode('utf-8')
        creds_dict = json.loads(creds_json)

        # Show which service account we're testing
        service_account_email = creds_dict.get('client_email', 'Unknown')
        project_id = creds_dict.get('project_id', 'Unknown')

        logger.info(f"🔍 Testing service account: {service_account_email}")
        logger.info(f"🔍 Project ID: {project_id}")

        # Create credentials
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=[
                'https://www.googleapis.com/auth/documents',
                'https://www.googleapis.com/auth/drive'
            ]
        )

        # Test Google Docs API
        logger.info("📄 Testing Google Docs API access...")
        docs_service = build('docs', 'v1', credentials=credentials)

        # Test Google Drive API
        logger.info("📁 Testing Google Drive API access...")
        drive_service = build('drive', 'v3', credentials=credentials)

        # Test folder access
        folder_id = "1Zrk26Mn0QtH9_9WYq4fPAaIdONOAIkcS"  # Your donor profiles folder
        logger.info(f"🔍 Testing access to folder: {folder_id}")

        try:
            folder_info = drive_service.files().get(fileId=folder_id).execute()
            logger.info(f"✅ Folder access successful: {folder_info.get('name', 'Unknown')}")
        except Exception as e:
            logger.error(f"❌ Folder access failed: {e}")
            return False

        # Test document creation
        logger.info("📝 Testing document creation...")

        test_doc = {
            'title': 'Service Account Test Document',
            'parents': [folder_id]
        }

        try:
            # Create the document
            document = docs_service.documents().create(body={'title': test_doc['title']}).execute()
            doc_id = document['documentId']
            logger.info(f"✅ Document created successfully: {doc_id}")

            # Move to folder
            drive_service.files().update(
                fileId=doc_id,
                addParents=folder_id,
                removeParents='root'
            ).execute()
            logger.info(f"✅ Document moved to folder successfully")

            # Add some content
            requests = [{
                'insertText': {
                    'location': {'index': 1},
                    'text': f'Test document created by service account: {service_account_email}\n\nThis confirms that the service account has proper permissions to create and edit documents in the donor profiles folder.'
                }
            }]

            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            logger.info(f"✅ Document content added successfully")

            # Clean up - delete the test document
            drive_service.files().delete(fileId=doc_id).execute()
            logger.info(f"✅ Test document deleted successfully")

            logger.info("🎉 ALL TESTS PASSED! Service account permissions are working correctly.")
            return True

        except Exception as e:
            logger.error(f"❌ Document creation failed: {e}")
            return False

    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        return False

def main():
    logger.info("🧪 Starting Google Docs Service Account Permission Test")
    logger.info("=" * 60)

    success = test_google_docs_permissions()

    logger.info("=" * 60)
    if success:
        logger.info("✅ RESULT: Service account permissions are working correctly!")
        logger.info("✅ Google Docs export should work in the donor profile generator")
    else:
        logger.info("❌ RESULT: Service account permissions need to be fixed")
        logger.info("❌ Please check:")
        logger.info("   1. Service account is added to the Google Drive folder")
        logger.info("   2. Service account has Editor permissions")
        logger.info("   3. Google Docs API and Google Drive API are enabled")

    return success

if __name__ == "__main__":
    main()