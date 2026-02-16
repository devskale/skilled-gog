#!/usr/bin/env python3
"""
Direct Google Docs Editor - Edit Google Docs programmatically using API
No intermediate formats needed - works directly with Google Docs structure
"""

import os
import sys

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

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

def get_document(doc_id, include_tabs_content=False):
    """Get full document structure"""
    try:
        creds = get_credentials()
        if not creds:
            return None
        
        service = build('docs', 'v1', credentials=creds)
        if include_tabs_content:
            document = service.documents().get(
                documentId=doc_id,
                includeTabsContent=True
            ).execute()
        else:
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

def add_table(doc_id, rows, cols, data=None, at_end=True, after_text=None):
    """Add a table to the document"""
    try:
        creds = get_credentials()
        if not creds:
            return False

        service = build('docs', 'v1', credentials=creds)
        doc = service.documents().get(documentId=doc_id).execute()

        # Find insert position
        if after_text:
            index = find_text_index(doc, after_text)
            if index is None:
                print(f"❌ Text '{after_text}' not found")
                return False
            insert_index = index + len(after_text)
        else:
            # Insert at end
            content = doc.get('body', {}).get('content', [])
            insert_index = content[-1].get('endIndex', 1) - 1

        requests = [
            {
                'insertTable': {
                    'rows': rows,
                    'columns': cols,
                    'location': {'index': insert_index}
                }
            }
        ]

        result = service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        print(f"✓ Added {rows}x{cols} table")
        return True
    except HttpError as e:
        print(f"❌ Error: {e}")
        return False

def delete_range(doc_id, start_index, end_index):
    """Delete content in a range"""
    try:
        creds = get_credentials()
        if not creds:
            return False

        service = build('docs', 'v1', credentials=creds)

        requests = [
            {
                'deleteContentRange': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': end_index
                    }
                }
            }
        ]

        service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        print(f"✓ Deleted range {start_index}-{end_index}")
        return True
    except HttpError as e:
        print(f"❌ Error: {e}")
        return False


def list_tabs(doc_id):
    """List all tabs in the document"""
    try:
        creds = get_credentials()
        if not creds:
            return None

        service = build('docs', 'v1', credentials=creds)
        doc = get_document(doc_id, include_tabs_content=True)

        if not doc:
            return None

        tabs = doc.get('tabs', [])

        if not tabs:
            print("No tabs found (document may not have tabs enabled)")
            return None

        print(f"\nDocument: {doc.get('title')}")
        print(f"Total tabs: {len(tabs)}")
        print("\nTab ID\t\t\t\tTitle\t\t\tType")
        print("-" * 70)

        def print_tab(tab, indent=0):
            props = tab.get('tabProperties', {})
            tab_id = props.get('tabId', 'N/A')
            title = props.get('title', 'Untitled')
            tab_type = 'documentTab' if 'documentTab' in tab else 'other'
            prefix = "  " * indent
            print(f"{prefix}{tab_id}\t{title}\t\t{tab_type}")

            # Recursively print child tabs
            for child in tab.get('childTabs', []):
                print_tab(child, indent + 1)

        for tab in tabs:
            print_tab(tab)

        return tabs
    except HttpError as e:
        print(f"❌ Error: {e}")
        return None


def create_tab(doc_id, title, parent_tab_id=None, index=None):
    """Create a new tab in the document"""
    try:
        creds = get_credentials()
        if not creds:
            return False

        service = build('docs', 'v1', credentials=creds)

        create_tab_request = {
            'createTab': {
                'tabProperties': {
                    'title': title
                }
            }
        }

        if parent_tab_id:
            create_tab_request['createTab']['tabProperties']['parentTabId'] = parent_tab_id

        if index is not None:
            create_tab_request['createTab']['tabProperties']['index'] = index

        requests = [create_tab_request]

        result = service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        print(f"✓ Created tab '{title}'")
        return True
    except HttpError as e:
        print(f"❌ Error: {e}")
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

        result = service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        print(f"✓ Deleted tab {tab_id}")
        return True
    except HttpError as e:
        print(f"❌ Error: {e}")
        return False


def rename_tab(doc_id, tab_id, new_title):
    """Rename a tab"""
    try:
        creds = get_credentials()
        if not creds:
            return False

        service = build('docs', 'v1', credentials=creds)

        requests = [
            {
                'updateTabProperties': {
                    'tabProperties': {
                        'tabId': tab_id,
                        'title': new_title
                    },
                    'fields': 'title'
                }
            }
        ]

        result = service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        print(f"✓ Renamed tab to '{new_title}'")
        return True
    except HttpError as e:
        print(f"❌ Error: {e}")
        return False


def get_all_tabs(doc):
    """Get flat list of all tabs including child tabs"""
    all_tabs = []

    def add_tab_and_children(tab):
        all_tabs.append(tab)
        for child in tab.get('childTabs', []):
            add_tab_and_children(child)

    for tab in doc.get('tabs', []):
        add_tab_and_children(tab)

    return all_tabs


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 gdocs_edit.py <command> <doc_id> [args...]")
        print("\nCommands:")
        print("  structure <doc_id>              - Show document structure")
        print("  append <doc_id> <text>          - Append text to document")
        print("  insert <doc_id> <after> <text>  - Insert text after specified text")
        print("  replace <doc_id> <old> <new>    - Replace text")
        print("  paragraph <doc_id> <text>       - Add new paragraph")
        print("  bold <doc_id> <text>            - Make text bold")
        print("  table <doc_id> <rows> <cols> [after] - Add table (optionally after text)")
        print("  delete <doc_id> <start> <end>   - Delete content range")
        print("\nTab Commands:")
        print("  tabs list <doc_id>              - List all tabs")
        print("  tabs create <doc_id> <title>    - Create new tab")
        print("  tabs delete <doc_id> <tab_id>   - Delete tab")
        print("  tabs rename <doc_id> <tab_id> <title> - Rename tab")
        print("\nYour doc ID: 1kJG9gFMy4M2iHfdxOhQ_KfNh1oy1P4aOdsDB-9626eg")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'structure':
        if len(sys.argv) < 3:
            print("❌ Error: structure requires doc_id")
            sys.exit(1)
        doc_id = sys.argv[2]
        doc = get_document(doc_id)
        if doc:
            print_document_structure(doc)
    elif command == 'append':
        if len(sys.argv) < 4:
            print("❌ Error: append requires doc_id and text")
            sys.exit(1)
        doc_id = sys.argv[2]
        text = sys.argv[3]
        append_text(doc_id, text)
    elif command == 'insert':
        if len(sys.argv) < 5:
            print("❌ Error: insert requires doc_id, after_text and new_text")
            sys.exit(1)
        doc_id = sys.argv[2]
        after_text = sys.argv[3]
        new_text = sys.argv[4]
        insert_after_text(doc_id, after_text, new_text)
    elif command == 'replace':
        if len(sys.argv) < 5:
            print("❌ Error: replace requires doc_id, old_text and new_text")
            sys.exit(1)
        doc_id = sys.argv[2]
        old_text = sys.argv[3]
        new_text = sys.argv[4]
        replace_text(doc_id, old_text, new_text)
    elif command == 'paragraph':
        if len(sys.argv) < 4:
            print("❌ Error: paragraph requires doc_id and text")
            sys.exit(1)
        doc_id = sys.argv[2]
        text = sys.argv[3]
        add_paragraph(doc_id, text)
    elif command == 'bold':
        if len(sys.argv) < 4:
            print("❌ Error: bold requires doc_id and text")
            sys.exit(1)
        doc_id = sys.argv[2]
        text = sys.argv[3]
        make_bold(doc_id, text)
    elif command == 'table':
        if len(sys.argv) < 5:
            print("❌ Error: table requires doc_id, rows and cols")
            sys.exit(1)
        doc_id = sys.argv[2]
        rows = int(sys.argv[3])
        cols = int(sys.argv[4])
        after_text = sys.argv[5] if len(sys.argv) > 5 else None
        add_table(doc_id, rows, cols, after_text=after_text)
    elif command == 'delete':
        if len(sys.argv) < 5:
            print("❌ Error: delete requires doc_id, start_index and end_index")
            sys.exit(1)
        doc_id = sys.argv[2]
        start_index = int(sys.argv[3])
        end_index = int(sys.argv[4])
        delete_range(doc_id, start_index, end_index)
    elif command == 'tabs':
        if len(sys.argv) < 4:
            print("❌ Error: tabs requires subcommand and doc_id")
            print("Usage: python3 gdocs_edit.py tabs <subcommand> <doc_id> [args...]")
            print("\nTab subcommands:")
            print("  list <doc_id>                   - List all tabs")
            print("  create <doc_id> <title>         - Create new tab")
            print("  delete <doc_id> <tab_id>        - Delete tab")
            print("  rename <doc_id> <tab_id> <title> - Rename tab")
            sys.exit(1)

        subcommand = sys.argv[2]
        doc_id = sys.argv[3]

        if subcommand == 'list':
            list_tabs(doc_id)
        elif subcommand == 'create':
            if len(sys.argv) < 5:
                print("❌ Error: tabs create requires doc_id and title")
                sys.exit(1)
            title = sys.argv[4]
            create_tab(doc_id, title)
        elif subcommand == 'delete':
            if len(sys.argv) < 5:
                print("❌ Error: tabs delete requires doc_id and tab_id")
                sys.exit(1)
            tab_id = sys.argv[4]
            delete_tab(doc_id, tab_id)
        elif subcommand == 'rename':
            if len(sys.argv) < 6:
                print("❌ Error: tabs rename requires doc_id, tab_id and new title")
                sys.exit(1)
            tab_id = sys.argv[4]
            new_title = sys.argv[5]
            rename_tab(doc_id, tab_id, new_title)
        else:
            print(f"❌ Unknown tabs subcommand: {subcommand}")
            sys.exit(1)
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
