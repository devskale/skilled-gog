#!/usr/bin/env python3
"""
Google Gmail API Reader - Read Gmail messages via API
"""

import os
import sys
import base64
import email
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/drive']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'client_secrets.json'

def get_credentials():
    """Get OAuth credentials for Gmail API"""
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
                return None

            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds

def list_messages(max_results=10, query='', label_ids=[]):
    """List Gmail messages"""
    try:
        creds = get_credentials()
        if not creds:
            return False

        service = build('gmail', 'v1', credentials=creds)

        # Build the request
        request = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q=query,
            labelIds=label_ids if label_ids else None
        )

        result = request.execute()
        messages = result.get('messages', [])

        print(f"✓ Found {len(messages)} messages")
        return messages

    except HttpError as e:
        print(f"❌ Error listing messages: {e}")
        if e.status_code == 403:
            print("   ⚠️ Gmail API is not enabled for this project")
            print("   Enable it at: https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=667256544145")
        return False

def get_message(message_id, format='full'):
    """Get a Gmail message by ID"""
    try:
        creds = get_credentials()
        if not creds:
            return False

        service = build('gmail', 'v1', credentials=creds)

        result = service.users().messages().get(
            userId='me',
            id=message_id,
            format=format
        ).execute()

        return result

    except HttpError as e:
        print(f"❌ Error getting message: {e}")
        return False

def get_message_body(message):
    """Extract the body text from a Gmail message"""
    payload = message.get('payload', {})

    # Try to get the body from different sources
    if 'body' in payload:
        if 'data' in payload['body']:
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

    # Check for parts
    if 'parts' in payload:
        for part in payload['parts']:
            # Check if this part has a body
            if 'body' in part and 'data' in part['body']:
                try:
                    data = base64.urlsafe_b64decode(part['body']['data'])
                    return data.decode('utf-8')
                except:
                    pass

            # Check for nested parts
            if 'parts' in part:
                for nested_part in part['parts']:
                    if 'body' in nested_part and 'data' in nested_part['body']:
                        try:
                            data = base64.urlsafe_b64decode(nested_part['body']['data'])
                            return data.decode('utf-8')
                        except:
                            pass

    return "[Body could not be extracted]"

def print_message_header(message):
    """Print message header information"""
    payload = message.get('payload', {})
    headers = payload.get('headers', [])

    header_dict = {}
    for h in headers:
        header_dict[h['name']] = h['value']

    subject = header_dict.get('Subject', '(No subject)')
    from_addr = header_dict.get('From', '(Unknown sender)')
    date = header_dict.get('Date', '(Unknown date)')

    print(f"\n{'='*80}")
    print(f"Subject: {subject}")
    print(f"From: {from_addr}")
    print(f"Date: {date}")
    print(f"ID: {message.get('id', 'Unknown')}")
    print(f"Labels: {', '.join(message.get('labelIds', []))}")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 google_gmail_api.py <command> [args...]")
        print("\nCommands:")
        print("  list [max_results] [query] [labels]  - List messages")
        print("  get <message_id>                   - Get a message")
        print("  body <message_id>                   - Get message body only")
        print("\nExamples:")
        print("  # List 10 most recent messages")
        print("  python3 google_gmail_api.py list")
        print("  # List 20 messages matching query")
        print("  python3 google_gmail_api.py list 20 'from:example.com'")
        print("  # Get specific message")
        print("  python3 google_gmail_api.py get 123456789abcdef")
        print("  # Get message body only")
        print("  python3 google_gmail_api.py body 123456789abcdef")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'list':
        max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        query = sys.argv[3] if len(sys.argv) > 3 else ''
        labels = sys.argv[4].split(',') if len(sys.argv) > 4 else []

        messages = list_messages(max_results, query, labels)

        if messages:
            for i, msg in enumerate(messages, 1):
                # Get full message for headers
                full_msg = get_message(msg['id'], format='metadata')
                if full_msg:
                    print_message_header(full_msg)
                    body = get_message_body(full_msg)
                    # Show first 500 chars of body
                    print(f"{body[:500]}...")
                    if len(body) > 500:
                        print(f"\n... ({len(body) - 500} more characters)")
                print("\n")

    elif command == 'get':
        if len(sys.argv) < 3:
            print("❌ Error: get command requires message_id")
            sys.exit(1)

        message_id = sys.argv[2]
        message = get_message(message_id)

        if message:
            print_message_header(message)
            body = get_message_body(message)
            print(body)

    elif command == 'body':
        if len(sys.argv) < 3:
            print("❌ Error: body command requires message_id")
            sys.exit(1)

        message_id = sys.argv[2]
        message = get_message(message_id)

        if message:
            body = get_message_body(message)
            print(body)

    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
