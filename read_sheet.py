#!/usr/bin/env python3
"""Read Google Sheet using Google Sheets API"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Sheet ID from BOM sheet
SHEET_ID = "1MYNuzKqGEQszGO5iegXMWBzis7zdTSdvg4F3-kFWm-Q"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_credentials():
    """Get OAuth credentials"""
    creds = None
    token_path = 'token.json'

    # Load existing token
    if os.path.exists(token_path):
        with open(token_path, 'r') as token:
            token_data = json.load(token)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)

    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds

def read_sheet(sheet_id):
    """Read the spreadsheet"""
    creds = get_credentials()

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Get spreadsheet info
        sheet_metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = sheet_metadata.get('sheets', '')
        print(f"Spreadsheet: {sheet_metadata.get('properties', {}).get('title', 'Unknown')}")
        print(f"Number of sheets: {len(sheets)}")
        print()

        # Read each sheet
        for sheet in sheets:
            properties = sheet.get('properties', {})
            title = properties.get('title', 'Unknown')
            sheet_id = properties.get('sheetId', 0)
            print(f"=== Sheet: {title} (ID: {sheet_id}) ===")

            # Read all data
            result = service.spreadsheets().values().get(
                spreadsheetId=SHEET_ID,
                range=title
            ).execute()

            values = result.get('values', [])

            if not values:
                print('No data found.')
            else:
                for i, row in enumerate(values[:50], 1):  # Limit to first 50 rows
                    print(f"Row {i}: {row}")
            print()

    except HttpError as err:
        print(f"Error accessing spreadsheet: {err}")

if __name__ == '__main__':
    print("Reading BOM Sheet...")
    print(f"Sheet ID: {SHEET_ID}")
    print()
    read_sheet(SHEET_ID)
