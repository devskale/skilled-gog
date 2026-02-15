#!/usr/bin/env python3
"""
Read and display detailed document structure from Google Doc
"""

import os
import sys
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
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

def extract_full_text_detailed(doc_id):
    """Extract all text with full details"""
    creds = get_credentials()
    service = build('docs', 'v1', credentials=creds)

    document = service.documents().get(documentId=doc_id).execute()

    print(f"📄 Document: {document.get('title')}")
    print(f"Document ID: {doc_id}")
    print(f"Revision ID: {document.get('revisionId')}")
    print(f"Total elements: {len(document.get('body', {}).get('content', []))}")
    print(f"{'='*80}")
    print()

    content = document.get('body', {}).get('content', [])

    for idx, element in enumerate(content):
        element_type = list(element.keys())[0] if element else 'unknown'

        if 'paragraph' in element:
            paragraph = element['paragraph']
            elements = paragraph.get('elements', [])
            text = ""

            # Get style info
            style = paragraph.get('paragraphStyle', {})
            named_style = style.get('namedStyleType', 'NORMAL')

            # Extract all text
            for elem in elements:
                if 'textRun' in elem:
                    text += elem['textRun']['content']
                    # Could also check for formatting here
                elif 'pageBreak' in elem:
                    text += "[PAGE BREAK]"
                elif 'columnBreak' in elem:
                    text += "[COLUMN BREAK]"

            if text.strip() or named_style != 'NORMAL':
                style_name = named_style.replace('_', ' ').title()
                print(f"[{idx:3d}] {style_name:20} | {text.strip()[:100]}")
            elif text.strip():
                print(f"[{idx:3d}] {'Normal':20} | {text.strip()[:100]}")

        elif 'table' in element:
            table = element['table']
            rows = len(table.get('tableRows', []))
            print(f"[{idx:3d}] Table            | {rows} rows")

        elif 'tableOfContents' in element:
            print(f"[{idx:3d}] Table of Contents")

        elif 'sectionBreak' in element:
            print(f"[{idx:3d}] Section Break")

        else:
            print(f"[{idx:3d}] {element_type:20} | {str(element)[:100]}")

    # Also save full JSON for inspection
    with open('doc_structure.json', 'w') as f:
        json.dump(document, f, indent=2)
    print(f"\n📁 Full document structure saved to: doc_structure.json")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 read_doc_detailed.py <doc_id>")
        sys.exit(1)

    doc_id = sys.argv[1]
    extract_full_text_detailed(doc_id)
