#!/usr/bin/env python3
"""
Direct Google Docs Editor - Edit Google Docs programmatically using API
No intermediate formats needed - works directly with Google Docs structure
"""

import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/documents']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'client_secrets.json'

def get_credentials():
    """Get OAuth credentials for Google Docs API"""
    creds = None
    
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print("❌ client_secrets.json not found!")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return creds

def get_document(doc_id):
    """Get full document structure"""
    try:
        creds = get_credentials()
        if not creds:
            return None
        
        service = build('docs', 'v1', credentials=creds)
        document = service.documents().get(documentId=doc_id).execute()
        
        return document
    except HttpError as e:
        print(f"❌ Error: {e}")
        return None

def print_document_structure(doc):
    """Print document structure for debugging"""
    content = doc.get('body', {}).get('content', [])
    print(f"Document: {doc.get('title')}")
    print(f"Total elements: {len(content)}")
    print()
    
    for i, element in enumerate(content):
        if 'paragraph' in element:
            para = element['paragraph']
            text = extract_text_from_paragraph(para)
            print(f"{i}: Paragraph - {text[:50]}...")
        elif 'table' in element:
            print(f"{i}: Table")
        elif 'sectionBreak' in element:
            print(f"{i}: Section Break")

def extract_text_from_paragraph(para):
    """Extract text from paragraph element"""
    text = ""
    for elem in para.get('elements', []):
        if 'textRun' in elem:
            text += elem['textRun']['content']
    return text

def find_text_index(doc, search_text):
    """Find the index of text in document"""
    content = doc.get('body', {}).get('content', [])
    current_index = 1
    
    for element in content:
        if 'paragraph' in element:
            para = element['paragraph']
            for elem in para.get('elements', []):
                if 'textRun' in elem:
                    text = elem['textRun']['content']
                    if search_text in text:
                        return current_index + text.index(search_text)
                    current_index += len(text)
    
    return None

def append_text(doc_id, text):
    """Append text to the end of document"""
    try:
        creds = get_credentials()
        if not creds:
            return False
        
        service = build('docs', 'v1', credentials=creds)
        
        # Get document length
        doc = service.documents().get(documentId=doc_id).execute()
        end_index = doc.get('body', {}).get('content', [{}])[-1].get('endIndex', 1) - 1
        
        requests = [
            {
                'insertText': {
                    'location': {'index': end_index},
                    'text': text
                }
            }
        ]
        
        result = service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        
        print(f"✓ Appended text to document")
        return True
    except HttpError as e:
        print(f"❌ Error: {e}")
        return False

def insert_after_text(doc_id, after_text, new_text):
    """Insert text after specific text"""
    try:
        creds = get_credentials()
        if not creds:
            return False
        
        service = build('docs', 'v1', credentials=creds)
        
        # Find position
        doc = service.documents().get(documentId=doc_id).execute()
        index = find_text_index(doc, after_text)
        
        if index is None:
            print(f"❌ Text '{after_text}' not found")
            return False
        
        # Calculate insert position (after the text)
        insert_index = index + len(after_text)
        
        requests = [
            {
                'insertText': {
                    'location': {'index': insert_index},
                    'text': new_text
                }
            }
        ]
        
        result = service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        
        print(f"✓ Inserted text after '{after_text}'")
        return True
    except HttpError as e:
        print(f"❌ Error: {e}")
        return False

def replace_text(doc_id, old_text, new_text):
    """Replace all occurrences of text"""
    try:
        creds = get_credentials()
        if not creds:
            return False
        
        service = build('docs', 'v1', credentials=creds)
        
        requests = [
            {
                'replaceAllText': {
                    'containsText': {'text': old_text},
                    'replaceText': new_text
                }
            }
        ]
        
        result = service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        
        print(f"✓ Replaced '{old_text}' with '{new_text}'")
        return True
    except HttpError as e:
        print(f"❌ Error: {e}")
        return False

def add_paragraph(doc_id, text):
    """Add a new paragraph at the end"""
    try:
        creds = get_credentials()
        if not creds:
            return False
        
        service = build('docs', 'v1', credentials=creds)
        
        # Get document length
        doc = service.documents().get(documentId=doc_id).execute()
        end_index = doc.get('body', {}).get('content', [{}])[-1].get('endIndex', 1) - 1
        
        requests = [
            {
                'insertText': {
                    'location': {'index': end_index},
                    'text': '\n' + text
                }
            }
        ]
        
        result = service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        
        print(f"✓ Added paragraph: {text[:50]}...")
        return True
    except HttpError as e:
        print(f"❌ Error: {e}")
        return False

def make_bold(doc_id, start_text, end_text=None):
    """Make text bold (from start_text to end_text or entire start_text)"""
    try:
        creds = get_credentials()
        if not creds:
            return False
        
        service = build('docs', 'v1', credentials=creds)
        
        doc = service.documents().get(documentId=doc_id).execute()
        start_index = find_text_index(doc, start_text)
        
        if start_index is None:
            print(f"❌ Text '{start_text}' not found")
            return False
        
        if end_text:
            end_index = find_text_index(doc, end_text) + len(end_text)
        else:
            end_index = start_index + len(start_text)
        
        requests = [
            {
                'updateTextStyle': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': end_index
                    },
                    'textStyle': {'bold': True},
                    'fields': 'bold'
                }
            }
        ]
        
        result = service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        
        print(f"✓ Made text bold")
        return True
    except HttpError as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 gdocs_edit.py <command> <doc_id> [args...]")
        print("\nCommands:")
        print("  append <doc_id> <text>          - Append text to document")
        print("  insert <doc_id> <after> <text>  - Insert text after specified text")
        print("  replace <doc_id> <old> <new>   - Replace text")
        print("  paragraph <doc_id> <text>       - Add new paragraph")
        print("  bold <doc_id> <text>           - Make text bold")
        print("  structure <doc_id>              - Show document structure")
        print("\nYour doc ID: 1kJG9gFMy4M2iHfdxOhQ_KfNh1oy1P4aOdsDB-9626eg")
        sys.exit(1)
    
    command = sys.argv[1]
    doc_id = sys.argv[2]
    
    if command == 'append':
        text = sys.argv[3] if len(sys.argv) > 3 else ''
        append_text(doc_id, text)
    elif command == 'insert':
        if len(sys.argv) < 5:
            print("❌ Error: insert command requires after_text and new_text")
            sys.exit(1)
        after_text = sys.argv[3]
        new_text = sys.argv[4]
        insert_after_text(doc_id, after_text, new_text)
    elif command == 'replace':
        if len(sys.argv) < 5:
            print("❌ Error: replace command requires old_text and new_text")
            sys.exit(1)
        old_text = sys.argv[3]
        new_text = sys.argv[4]
        replace_text(doc_id, old_text, new_text)
    elif command == 'paragraph':
        text = sys.argv[3] if len(sys.argv) > 3 else ''
        add_paragraph(doc_id, text)
    elif command == 'bold':
        text = sys.argv[3] if len(sys.argv) > 3 else ''
        make_bold(doc_id, text)
    elif command == 'structure':
        doc = get_document(doc_id)
        if doc:
            print_document_structure(doc)
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
