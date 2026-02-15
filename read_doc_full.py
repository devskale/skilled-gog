#!/usr/bin/env python3
"""
Comprehensive reader for Google Docs - reads ALL content types
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

def print_element(element, indent=0):
    """Recursively print element with full details"""
    prefix = "  " * indent

    if 'paragraph' in element:
        para = element['paragraph']
        style = para.get('paragraphStyle', {})
        named_style = style.get('namedStyleType', 'NORMAL')
        alignment = style.get('alignment', 'START')

        # Get all text from paragraph
        text_parts = []
        elements = para.get('elements', [])
        for elem in elements:
            if 'textRun' in elem:
                content = elem['textRun']['content']
                text_style = elem['textRun'].get('textStyle', {})
                bold = text_style.get('bold', False)
                italic = text_style.get('italic', False)
                link = text_style.get('link', {}).get('url', '')
                if content.strip():
                    text_parts.append(content.rstrip('\n'))
            elif 'pageBreak' in elem:
                text_parts.append('[PAGE BREAK]')
            elif 'columnBreak' in elem:
                text_parts.append('[COLUMN BREAK]')
            elif 'horizontalRule' in elem:
                text_parts.append('---')

        text = ''.join(text_parts).strip()
        if text:
            print(f"{prefix}[PARAGRAPH] Style: {named_style}, Align: {alignment}")
            print(f"{prefix}{text}")

        # Check for bullet/numbered list
        bullet = para.get('bullet')
        if bullet:
            list_id = bullet.get('listId', 'unknown')
            nesting_level = bullet.get('nestingLevel', 0)
            print(f"{prefix}  → List: {list_id}, Level: {nesting_level}")

    elif 'table' in element:
        table = element['table']
        rows = table.get('tableRows', [])
        print(f"{prefix}[TABLE] {len(rows)} rows")
        for row_idx, row in enumerate(rows[:10]):  # First 10 rows
            cells = row.get('tableCells', [])
            row_text = []
            for cell in cells:
                cell_text = ""
                cell_content = cell.get('content', [])
                for cell_elem in cell_content:
                    if 'paragraph' in cell_elem:
                        para = cell_elem['paragraph']
                        for para_elem in para.get('elements', []):
                            if 'textRun' in para_elem:
                                cell_text += para_elem['textRun']['content']
                row_text.append(cell_text.strip()[:40])
            if any(row_text):  # Only print if row has content
                print(f"{prefix}  Row {row_idx}: {' | '.join(row_text)}")

    elif 'tableOfContents' in element:
        print(f"{prefix}[TABLE OF CONTENTS]")

    elif 'sectionBreak' in element:
        print(f"{prefix}[SECTION BREAK]")

    elif 'image' in element:
        img_props = element['image'].get('imageProperties', {})
        source_uri = img_props.get('contentUri', 'no URI')
        print(f"{prefix}[IMAGE] URI: {source_uri[:60]}...")

    elif 'embeddedObject' in element:
        print(f"{prefix}[EMBEDDED OBJECT]")

    else:
        unknown_key = list(element.keys())[0] if element else 'unknown'
        print(f"{prefix}[{unknown_key.upper()}]")

def read_document_full(doc_id):
    """Read and display all document content"""
    creds = get_credentials()
    service = build('docs', 'v1', credentials=creds)

    document = service.documents().get(documentId=doc_id).execute()

    print("=" * 80)
    print(f"📄 DOCUMENT: {document.get('title')}")
    print(f"📎 ID: {doc_id}")
    print(f"📝 Revision: {document.get('revisionId')}")
    print(f"📊 Total elements: {len(document.get('body', {}).get('content', []))}")
    print(f"📄 Suggested revision ID: {document.get('suggestedRevisionId', 'None')}")
    print("=" * 80)
    print()

    content = document.get('body', {}).get('content', [])

    for idx, element in enumerate(content):
        print(f"Element #{idx}:")
        print_element(element, indent=1)
        print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 read_doc_full.py <doc_id>")
        sys.exit(1)

    doc_id = sys.argv[1]
    read_document_full(doc_id)
