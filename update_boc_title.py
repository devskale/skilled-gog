#!/usr/bin/env python3
"""
Update BOC document - first page title only
"""

import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/documents']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'client_secrets.json'

def get_credentials():
    """Get OAuth credentials"""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return creds

def update_boc_title_page(doc_id):
    """Update BOC document - first page only"""
    creds = get_credentials()
    service = build('docs', 'v1', credentials=creds)

    # Get current document
    document = service.documents().get(documentId=doc_id).execute()
    end_index = document.get('body', {}).get('content', [{}])[-1].get('endIndex', 2) - 1

    # Clear all content and replace with title page only
    requests = [
        # Delete all existing content
        {
            'deleteContentRange': {
                'range': {
                    'startIndex': 1,
                    'endIndex': end_index
                }
            }
        },
        # Insert new content
        {
            'insertText': {
                'location': {'index': 1},
                'text': '\n\nPflichtenheft\n\n\n\nAutor: hans@sylents.de\n\nsylents DE kontaktdaten\n\n'
            }
        }
    ]

    # Format title
    requests.extend([
        {
            'updateParagraphStyle': {
                'range': {
                    'startIndex': 3,
                    'endIndex': 15
                },
                'paragraphStyle': {
                    'namedStyleType': 'HEADING_1',
                    'alignment': 'CENTER'
                },
                'fields': 'namedStyleType,alignment'
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': 3,
                    'endIndex': 15
                },
                'textStyle': {
                    'bold': True,
                    'fontSize': {
                        'magnitude': 24,
                        'unit': 'PT'
                    }
                },
                'fields': 'bold,fontSize'
            }
        },
        # Center author line
        {
            'updateParagraphStyle': {
                'range': {
                    'startIndex': 17,
                    'endIndex': 40
                },
                'paragraphStyle': {
                    'alignment': 'CENTER'
                },
                'fields': 'alignment'
            }
        },
        # Center kontaktdaten line
        {
            'updateParagraphStyle': {
                'range': {
                    'startIndex': 42,
                    'endIndex': 64
                },
                'paragraphStyle': {
                    'alignment': 'CENTER'
                },
                'fields': 'alignment'
            }
        }
    ])

    # Execute batch update
    result = service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': requests}
    ).execute()

    print(f"✓ BOC document updated - first page only")
    print(f"  View at: https://docs.google.com/document/d/{doc_id}/edit")

if __name__ == '__main__':
    doc_id = '1kJG9gFMy4M2iHfdxOhQ_KfNh1oy1P4aOdsDB-9626eg'
    update_boc_title_page(doc_id)
