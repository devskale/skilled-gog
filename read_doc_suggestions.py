#!/usr/bin/env python3
"""
Read suggestions, headers, footers, and comments from Google Doc
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

def extract_text_from_paragraphs(content):
    """Extract all text from paragraph content"""
    text = ""
    for element in content:
        if 'paragraph' in element:
            para = element['paragraph']
            for elem in para.get('elements', []):
                if 'textRun' in elem:
                    text += elem['textRun']['content']
        elif 'table' in element:
            table = element['table']
            for row in table.get('tableRows', []):
                for cell in row.get('tableCells', []):
                    cell_text = extract_text_from_paragraphs(cell.get('content', []))
                    text += cell_text + " | "
            text += "\n"
    return text

def read_document_suggestions(doc_id):
    """Read document including suggestions, headers, footers"""
    creds = get_credentials()
    service = build('docs', 'v1', credentials=creds)

    document = service.documents().get(documentId=doc_id).execute()

    print("=" * 80)
    print(f"📄 DOCUMENT: {document.get('title')}")
    print("=" * 80)
    print()

    # Check headers
    if 'headers' in document:
        print("📌 HEADERS:")
        for key, header in document['headers'].items():
            content = header.get('content', [])
            text = extract_text_from_paragraphs(content)
            if text.strip():
                print(f"  Header {key}:")
                print(f"  {text[:200]}")
        print()

    # Check footers
    if 'footers' in document:
        print("📌 FOOTERS:")
        for key, footer in document['footers'].items():
            content = footer.get('content', [])
            text = extract_text_from_paragraphs(content)
            if text.strip():
                print(f"  Footer {key}:")
                print(f"  {text[:200]}")
        print()

    # Check document style for page size (to estimate pages)
    doc_style = document.get('documentStyle', {})
    page_size = doc_style.get('pageSize', {})
    width = page_size.get('width', {}).get('magnitude', 0)
    height = page_size.get('height', {}).get('magnitude', 0)
    print(f"📏 Page size: {width:.0f}pt x {height:.0f}pt (A4)")
    print()

    # Check suggestions
    content = document.get('body', {}).get('content', [])
    has_suggestions = False

    for idx, element in enumerate(content):
        if 'paragraph' in element:
            para = element['paragraph']
            elements = para.get('elements', [])

            for elem in elements:
                # Check for suggested changes
                if 'suggestedTextRuns' in elem:
                    has_suggestions = True
                    print(f"💡 SUGGESTION in element {idx}:")
                    for suggestion in elem.get('suggestedTextRuns', []):
                        text_run = suggestion.get('textRun', {})
                        suggestion_content = text_run.get('content', '')
                        if suggestion_content.strip():
                            print(f"  {suggestion_content[:200]}")
                    print()

                # Check for suggested deletion
                if 'suggestedDeletionIds' in elem:
                    has_suggestions = True
                    print(f"❌ SUGGESTED DELETION in element {idx}")

                # Check for suggested insertions
                if 'suggestedInsertionIds' in elem:
                    has_suggestions = True
                    print(f"➕ SUGGESTED INSERTION in element {idx}")

                # Check for paragraph style suggestions
                para_style = para.get('paragraphStyle', {})
                if 'suggestedParagraphStyleChanges' in para_style:
                    has_suggestions = True
                    print(f"📝 SUGGESTED STYLE CHANGE in element {idx}")

    if not has_suggestions:
        print("📌 No suggestions found")

    print()

    # Check for embedded objects with content
    print("📌 CHECKING FOR EMBEDDED OBJECTS:")
    for idx, element in enumerate(content):
        if 'embeddedObject' in element:
            print(f"  Element {idx}: Embedded Object")
            obj = element['embeddedObject']
            print(f"    Type: {obj.get('objectType', 'unknown')}")

        if 'image' in element:
            print(f"  Element {idx}: Image")

        if 'table' in element:
            table = element['table']
            rows = len(table.get('tableRows', []))
            print(f"  Element {idx}: Table with {rows} rows")

    print()
    print("📌 SUGGESTED REVISION ID:", document.get('suggestedRevisionId', 'None'))

    # Save full doc for inspection
    with open('doc_full.json', 'w') as f:
        json.dump(document, f, indent=2, ensure_ascii=False)
    print()
    print("📁 Full document saved to: doc_full.json")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 read_doc_suggestions.py <doc_id>")
        sys.exit(1)

    doc_id = sys.argv[1]
    read_document_suggestions(doc_id)
