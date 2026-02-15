#!/usr/bin/env python3
"""
Google Docs API Editor - Download and Edit Google Docs via API
"""

import os
import sys
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'client_secrets.json'

def get_credentials():
    """Get OAuth credentials for Google Docs API"""
    creds = None
    
    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print("❌ client_secrets.json not found!")
                print("\n📋 Setup Instructions:")
                print("1. Go to: https://console.cloud.google.com/")
                print("2. Create a new project or select existing one")
                print("3. Enable the Google Docs API:")
                print("   https://console.cloud.google.com/apis/library/docs.googleapis.com")
                print("4. Create OAuth 2.0 credentials:")
                print("   - Go to: Credentials → Create Credentials → OAuth client ID")
                print("   - Application type: Desktop application")
                print("   - Download the JSON file")
                print("5. Save the downloaded file as: client_secrets.json")
                print("6. Place it in this directory: " + os.getcwd())
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return creds

def download_document(doc_id, output_file='downloaded_doc.txt', format='txt'):
    """Download a Google Doc in specified format"""
    try:
        creds = get_credentials()
        if not creds:
            return False
        
        if format == 'docx':
            service = build('drive', 'v3', credentials=creds)
            
            mime_types = {
                'txt': 'text/plain',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'pdf': 'application/pdf'
            }
            
            mime_type = mime_types.get(format, 'text/plain')
            
            request = service.files().export_media(
                fileId=doc_id,
                mimeType=mime_type
            )
            
            with open(output_file, 'wb') as f:
                f.write(request.execute())
            
            print(f"✓ Downloaded document to: {output_file}")
            print(f"  Format: {format}")
            return True
        else:
            service = build('docs', 'v1', credentials=creds)
            document = service.documents().get(documentId=doc_id).execute()
            
            text_content = extract_text(document)
            
            with open(output_file, 'w') as f:
                f.write(text_content)
            
            print(f"✓ Downloaded document to: {output_file}")
            print(f"  Title: {document.get('title', 'Unknown')}")
            return True
        
    except HttpError as e:
        print(f"❌ Error accessing document: {e}")
        if e.status_code == 403:
            print("   You don't have permission to access this document")
        elif e.status_code == 404:
            print("   Document not found. Check the document ID")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def extract_text(document):
    """Recursively extract text from Google Doc structure"""
    text_content = ""
    content = document.get('body', {}).get('content', [])
    
    for element in content:
        if 'paragraph' in element:
            paragraph = element['paragraph']
            for elem in paragraph.get('elements', []):
                if 'textRun' in elem:
                    text_content += elem['textRun']['content']
        elif 'table' in element:
            table = element['table']
            for row in table.get('tableRows', []):
                for cell in row.get('tableCells', []):
                    for elem in cell.get('content', []):
                        if 'paragraph' in elem:
                            for p_elem in elem['paragraph'].get('elements', []):
                                if 'textRun' in p_elem:
                                    text_content += p_elem['textRun']['content']
                text_content += "\n"
    
    return text_content

def upload_document(doc_id, input_file, format='txt'):
    """Upload content back to Google Doc"""
    try:
        creds = get_credentials()
        if not creds:
            return False
        
        if format == 'docx':
            service = build('drive', 'v3', credentials=creds)
            
            # For DOCX, we upload as a new revision
            file_metadata = {'name': 'Uploaded Document'}
            media = MediaFileUpload(input_file, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            
            # Note: This creates a new file, doesn't update the existing doc
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            print(f"⚠️ Created new file (can't directly update Google Doc with DOCX)")
            print(f"  New file ID: {file.get('id')}")
            print(f"  View at: https://docs.google.com/document/d/{file.get('id')}/edit")
            return True
        else:
            # Read the file
            with open(input_file, 'r') as f:
                new_content = f.read()
            
            service = build('docs', 'v1', credentials=creds)
            
            # Get current document
            document = service.documents().get(documentId=doc_id).execute()
            
            # Clear existing content and replace with new text
            requests = [
                {
                    'deleteContentRange': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': document.get('body', {}).get('content', [{}])[-1].get('endIndex', 1) - 1
                        }
                    }
                },
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': new_content
                    }
                }
            ]
            
            result = service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            print(f"✓ Uploaded content to Google Doc")
            print(f"  Title: {document.get('title', 'Unknown')}")
            return True
        
    except HttpError as e:
        print(f"❌ Error uploading document: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 google_docs_api.py <command> <doc_id> [file] [format]")
        print("\nCommands:")
        print("  download <doc_id> [output_file] [format]  - Download document (format: txt, docx, pdf)")
        print("  upload <doc_id> <input_file> [format]     - Upload document (format: txt, docx)")
        print("\nYour doc ID: 1kJG9gFMy4M2iHfdxOhQ_KfNh1oy1P4aOdsDB-9626eg")
        sys.exit(1)
    
    command = sys.argv[1]
    doc_id = sys.argv[2]
    
    if command == 'download':
        output_file = sys.argv[3] if len(sys.argv) > 3 else 'downloaded_doc.txt'
        format = sys.argv[4] if len(sys.argv) > 4 else 'txt'
        if format != 'txt' and not output_file.endswith(f'.{format}'):
            output_file = output_file.rsplit('.', 1)[0] + f'.{format}' if '.' in output_file else f'{output_file}.{format}'
        success = download_document(doc_id, output_file, format)
    elif command == 'upload':
        if len(sys.argv) < 4:
            print("❌ Error: upload command requires input file")
            sys.exit(1)
        input_file = sys.argv[3]
        format = sys.argv[4] if len(sys.argv) > 4 else 'txt'
        if input_file.endswith('.docx'):
            format = 'docx'
        success = upload_document(doc_id, input_file, format)
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
    
    sys.exit(0 if success else 1)
