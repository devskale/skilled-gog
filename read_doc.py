#!/usr/bin/env python3
"""
Read full text content from Google Doc via API
"""

import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/documents.readonly', 'https://www.googleapis.com/auth/drive.readonly']
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

def extract_full_text(doc_id):
    """Extract all text from document with structure"""
    creds = get_credentials()
    service = build('docs', 'v1', credentials=creds)

    document = service.documents().get(documentId=doc_id).execute()

    print(f"📄 Document: {document.get('title')}")
    print(f"{'='*80}")
    print()

    content = document.get('body', {}).get('content', [])

    for element in content:
        if 'paragraph' in element:
            paragraph = element['paragraph']
            text_elements = paragraph.get('elements', [])
            text = ""
            is_heading = False
            heading_level = ""

            # Check for heading
            style = paragraph.get('paragraphStyle', {})
            named_style = style.get('namedStyleType', '')
            if 'HEADING' in named_style:
                is_heading = True
                heading_level = named_style.replace('HEADING_', '')

            # Extract text
            for elem in text_elements:
                if 'textRun' in elem:
                    text += elem['textRun']['content']

            if text.strip():
                if is_heading:
                    marker = "#" * int(heading_level) if heading_level.isdigit() else "#"
                    print(f"{marker} {text.strip()}")
                else:
                    print(text.strip())

        elif 'table' in element:
            table = element['table']
            rows = table.get('tableRows', [])
            for row_idx, row in enumerate(rows):
                row_text = []
                cells = row.get('tableCells', [])
                for cell in cells:
                    cell_text = ""
                    cell_content = cell.get('content', [])
                    for cell_elem in cell_content:
                        if 'paragraph' in cell_elem:
                            para = cell_elem['paragraph']
                            for para_elem in para.get('elements', []):
                                if 'textRun' in para_elem:
                                    cell_text += para_elem['textRun']['content']
                    row_text.append(cell_text.strip())
                print(f"  {' | '.join(row_text)}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 read_doc.py <doc_id>")
        sys.exit(1)

    doc_id = sys.argv[1]
    extract_full_text(doc_id)
