#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct Google Docs Editor - Edit Google Docs programmatically using API
No intermediate formats needed - works directly with Google Docs structure
"""

import os
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'client_secrets.json'

def find_credentials_file():
    """Find client_secrets.json in multiple locations"""
    search_paths = [
        CREDENTIALS_FILE,  # Current directory
        os.path.join('.agents/skills/google-workspace', CREDENTIALS_FILE),
        os.path.join(os.path.dirname(__file__), '.agents/skills/google-workspace', CREDENTIALS_FILE),
    ]
    for path in search_paths:
        if os.path.exists(path):
            return path
    return None

def get_credentials():
    """Get OAuth credentials for Google Docs API"""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds_file = find_credentials_file()
            if not creds_file:
                print("X client_secrets.json not found!")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w', encoding='utf-8') as token:
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
        print(f"[ERR] Error: {e}")
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
        
        print(f"[OK] Appended text to document")
        return True
    except HttpError as e:
        print(f"[ERR] Error: {e}")
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
            print(f"[ERR] Text '{after_text}' not found")
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
        
        print(f"[OK] Inserted text after '{after_text}'")
        return True
    except HttpError as e:
        print(f"[ERR] Error: {e}")
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
        
        print(f"[OK] Replaced '{old_text}' with '{new_text}'")
        return True
    except HttpError as e:
        print(f"[ERR] Error: {e}")
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
        
        print(f"[OK] Added paragraph: {text[:50]}...")
        return True
    except HttpError as e:
        print(f"[ERR] Error: {e}")
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
            print(f"[ERR] Text '{start_text}' not found")
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

        print(f"[OK] Made text bold")
        return True
    except HttpError as e:
        print(f"[ERR] Error: {e}")
        return False


def copy_document(doc_id, new_name=None):
    """Copy a document (for WORK versions) using Drive API"""
    try:
        creds = get_credentials()
        if not creds:
            return None

        # Use Drive API to copy
        drive_service = build('drive', 'v3', credentials=creds)

        # Get original document name if no new name provided
        if not new_name:
            original = drive_service.files().get(fileId=doc_id, fields='name').execute()
            new_name = f"{original['name']} - WORK-Kopie"

        # Copy the document
        copy_metadata = {'name': new_name}
        copied_file = drive_service.files().copy(
            fileId=doc_id,
            body=copy_metadata
        ).execute()

        new_id = copied_file['id']
        print(f"[OK] Document copied successfully")
        print(f"  New name: {new_name}")
        print(f"  New ID: {new_id}")
        print(f"  URL: https://docs.google.com/document/d/{new_id}/edit")

        return new_id
    except HttpError as e:
        print(f"[ERR] Error: {e}")
        return None


def insert_document(doc_id, folder_id):
    """Move/insert a document into a folder"""
    try:
        creds = get_credentials()
        if not creds:
            return False

        drive_service = build('drive', 'v3', credentials=creds)

        # Get current parents
        file = drive_service.files().get(fileId=doc_id, fields='parents, name').execute()
        previous_parents = ','.join(file.get('parents', []))
        doc_name = file.get('name', 'Unknown')

        # Move to new folder
        drive_service.files().update(
            fileId=doc_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()

        print(f"[OK] Document moved to folder")
        print(f"  Document: {doc_name}")
        print(f"  Folder ID: {folder_id}")
        return True
    except HttpError as e:
        print(f"[ERR] Error: {e}")
        return False


def rename_document(doc_id, new_name):
    """Rename a document"""
    try:
        creds = get_credentials()
        if not creds:
            return False

        drive_service = build('drive', 'v3', credentials=creds)

        # Get old name
        file = drive_service.files().get(fileId=doc_id, fields='name').execute()
        old_name = file.get('name', 'Unknown')

        # Rename
        drive_service.files().update(
            fileId=doc_id,
            body={'name': new_name},
            fields='name'
        ).execute()

        print(f"[OK] Document renamed")
        print(f"  Old name: {old_name}")
        print(f"  New name: {new_name}")
        return True
    except HttpError as e:
        print(f"[ERR] Error: {e}")
        return False


def delete_document(doc_id):
    """Move a document to trash (soft delete)"""
    try:
        creds = get_credentials()
        if not creds:
            return False

        drive_service = build('drive', 'v3', credentials=creds)

        # Get document name before deleting
        file = drive_service.files().get(fileId=doc_id, fields='name').execute()
        doc_name = file.get('name', 'Unknown')

        # Move to trash
        drive_service.files().update(
            fileId=doc_id,
            body={'trashed': True},
            fields='id, trashed'
        ).execute()

        print(f"[OK] Document moved to trash")
        print(f"  Name: {doc_name}")
        print(f"  ID: {doc_id}")
        print(f"  Restore: Use Google Drive Trash to restore")
        return True
    except HttpError as e:
        print(f"[ERR] Error: {e}")
        return False


# ============================================================================
# Tab Functions
# ============================================================================

def list_tabs(doc_id):
    """List all tabs in a document"""
    try:
        creds = get_credentials()
        if not creds:
            return None

        service = build('docs', 'v1', credentials=creds)
        doc = service.documents().get(documentId=doc_id, includeTabsContent=True).execute()

        tabs = doc.get('tabs', [])
        doc_title = doc.get('title', 'Untitled')

        print(f"[OK] Tabs in document: {doc_title}")
        if not tabs:
            print("  No tabs found (document uses single tab)")
            return []

        for i, tab in enumerate(tabs):
            tab_props = tab.get('tabProperties', {})
            tab_id = tab_props.get('tabId', 'unknown')
            tab_title = tab_props.get('title', 'Untitled')
            parent = tab_props.get('parentTabId', None)
            indent = "  " if parent else ""
            print(f"{indent}  [{i}] {tab_title} (ID: {tab_id})")

        return tabs
    except HttpError as e:
        print(f"[ERR] Error: {e}")
        return None


def create_tab(doc_id, title, parent_tab_id=None, index=None):
    """Create a new tab in the document"""
    try:
        creds = get_credentials()
        if not creds:
            return False

        service = build('docs', 'v1', credentials=creds)

        # Build createTab request
        tab_properties = {'title': title}
        if parent_tab_id:
            tab_properties['parentTabId'] = parent_tab_id
        if index is not None:
            tab_properties['index'] = index

        requests = [
            {
                'addDocumentTab': {
                    'tabProperties': tab_properties
                }
            }
        ]

        result = service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        # Get the new tab ID from the response
        replies = result.get('replies', [])
        if replies and 'addDocumentTab' in replies[0]:
            new_tab_id = replies[0]['addDocumentTab'].get('tabId', 'unknown')
            print(f"[OK] Tab created successfully")
            print(f"  Title: {title}")
            print(f"  Tab ID: {new_tab_id}")
            return new_tab_id
        else:
            print(f"[OK] Tab created: {title}")
            return True

    except HttpError as e:
        print(f"[ERR] Error: {e}")
        return False


def delete_tab(doc_id, tab_id):
    """Delete a tab from the document"""
    try:
        creds = get_credentials()
        if not creds:
            return False

        service = build('docs', 'v1', credentials=creds)

        requests = [
            {
                'deleteTab': {
                    'tabId': tab_id
                }
            }
        ]

        service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        print(f"[OK] Tab deleted")
        print(f"  Tab ID: {tab_id}")
        return True

    except HttpError as e:
        print(f"[ERR] Error: {e}")
        return False


def rename_tab(doc_id, tab_id, new_title):
    """Rename a tab in the document"""
    try:
        creds = get_credentials()
        if not creds:
            return False

        service = build('docs', 'v1', credentials=creds)

        requests = [
            {
                'updateDocumentTabProperties': {
                    'tabProperties': {
                        'tabId': tab_id,
                        'title': new_title
                    },
                    'fields': 'title'
                }
            }
        ]

        service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        print(f"[OK] Tab renamed successfully")
        print(f"  Tab ID: {tab_id}")
        print(f"  New Title: {new_title}")
        return True

    except HttpError as e:
        print(f"[ERR] Error: {e}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 gdocs_edit.py <command> <doc_id> [args...]")
        print("\nCommands:")
        print("  append <doc_id> <text>          - Append text to document")
        print("  insert <doc_id> <after> <text>  - Insert text after specified text")
        print("  replace <doc_id> <old> <new>    - Replace text")
        print("  paragraph <doc_id> <text>       - Add new paragraph")
        print("  bold <doc_id> <text>            - Make text bold")
        print("  structure <doc_id>              - Show document structure")
        print("\nDrive Commands (document management):")
        print("  copy <doc_id> [name]            - Copy document (default: - WORK-Kopie)")
        print("  rename <doc_id> <new_name>      - Rename document")
        print("  move <doc_id> <folder_id>       - Move document to folder")
        print("  delete <doc_id>                 - Move document to trash")
        print("\nTab Commands:")
        print("  tabs-list <doc_id>              - List all tabs")
        print("  tabs-create <doc_id> <title>    - Create new tab")
        print("  tabs-delete <doc_id> <tab_id>   - Delete tab")
        print("  tabs-rename <doc_id> <tab_id> <title> - Rename tab")
        print("\nYour doc ID: 1kJG9gFMy4M2iHfdxOhQ_KfNh1oy1P4aOdsDB-9626eg")
        sys.exit(1)

    command = sys.argv[1]

    # Commands without doc_id
    if command in ['help', '--help', '-h']:
        print("Usage: python3 gdocs_edit.py <command> <doc_id> [args...]")
        print("\nCommands:")
        print("  append <doc_id> <text>          - Append text to document")
        print("  insert <doc_id> <after> <text>  - Insert text after specified text")
        print("  replace <doc_id> <old> <new>    - Replace text")
        print("  paragraph <doc_id> <text>       - Add new paragraph")
        print("  bold <doc_id> <text>            - Make text bold")
        print("  structure <doc_id>              - Show document structure")
        print("\nDrive Commands (document management):")
        print("  copy <doc_id> [name]            - Copy document (default: - WORK-Kopie)")
        print("  rename <doc_id> <new_name>      - Rename document")
        print("  move <doc_id> <folder_id>       - Move document to folder")
        print("  delete <doc_id>                 - Move document to trash")
        print("\nTab Commands:")
        print("  tabs-list <doc_id>              - List all tabs")
        print("  tabs-create <doc_id> <title>    - Create new tab")
        print("  tabs-delete <doc_id> <tab_id>   - Delete tab")
        print("  tabs-rename <doc_id> <tab_id> <title> - Rename tab")
        sys.exit(0)

    if len(sys.argv) < 3:
        print("[ERR] Error: doc_id required")
        sys.exit(1)

    doc_id = sys.argv[2]

    if command == 'append':
        text = sys.argv[3] if len(sys.argv) > 3 else ''
        append_text(doc_id, text)
    elif command == 'insert':
        if len(sys.argv) < 5:
            print("[ERR] Error: insert command requires after_text and new_text")
            sys.exit(1)
        after_text = sys.argv[3]
        new_text = sys.argv[4]
        insert_after_text(doc_id, after_text, new_text)
    elif command == 'replace':
        if len(sys.argv) < 5:
            print("[ERR] Error: replace command requires old_text and new_text")
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
    elif command == 'copy':
        new_name = sys.argv[3] if len(sys.argv) > 3 else None
        copy_document(doc_id, new_name)
    elif command == 'rename':
        if len(sys.argv) < 4:
            print("[ERR] Error: rename command requires new_name")
            sys.exit(1)
        new_name = sys.argv[3]
        rename_document(doc_id, new_name)
    elif command == 'move':
        if len(sys.argv) < 4:
            print("[ERR] Error: move command requires folder_id")
            sys.exit(1)
        folder_id = sys.argv[3]
        insert_document(doc_id, folder_id)
    elif command == 'delete':
        delete_document(doc_id)
    elif command == 'tabs-list':
        list_tabs(doc_id)
    elif command == 'tabs-create':
        if len(sys.argv) < 4:
            print("[ERR] Error: tabs-create requires title")
            sys.exit(1)
        title = sys.argv[3]
        create_tab(doc_id, title)
    elif command == 'tabs-delete':
        if len(sys.argv) < 4:
            print("[ERR] Error: tabs-delete requires tab_id")
            sys.exit(1)
        tab_id = sys.argv[3]
        delete_tab(doc_id, tab_id)
    elif command == 'tabs-rename':
        if len(sys.argv) < 5:
            print("[ERR] Error: tabs-rename requires tab_id and new_title")
            sys.exit(1)
        tab_id = sys.argv[3]
        new_title = sys.argv[4]
        rename_tab(doc_id, tab_id, new_title)
    else:
        print(f"[ERR] Unknown command: {command}")
        sys.exit(1)
