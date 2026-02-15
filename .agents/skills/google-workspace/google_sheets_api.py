#!/usr/bin/env python3
"""
Google Sheets API - Read and Edit Google Sheets via API
"""

import os
import sys
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'client_secrets.json'

def get_credentials():
    """Get OAuth credentials for Google Sheets API"""
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
                print("3. Enable the Google Sheets API:")
                print("   https://console.cloud.google.com/apis/library/sheets.googleapis.com")
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

def read_sheet(sheet_id, range_name=None, output_file=None):
    """Read a Google Sheet"""
    try:
        creds = get_credentials()
        if not creds:
            return False
        
        service = build('sheets', 'v4', credentials=creds)
        
        # Get spreadsheet metadata
        sheet_metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = sheet_metadata.get('sheets', [])
        
        title = sheet_metadata.get('properties', {}).get('title', 'Unknown')
        print(f"✓ Spreadsheet: {title}")
        print(f"  URL: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
        print(f"  Number of sheets: {len(sheets)}")
        print()
        
        # Read data
        if range_name:
            # Read specific range
            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            values = result.get('values', [])
            
            print(f"=== Range: {range_name} ===")
            print_values(values)
            
            if output_file:
                save_to_file(values, output_file)
        else:
            # Read all sheets
            for sheet in sheets:
                properties = sheet.get('properties', {})
                sheet_title = properties.get('title', 'Unknown')
                sheet_id_local = properties.get('sheetId', 0)
                
                print(f"=== Sheet: {sheet_title} (ID: {sheet_id_local}) ===")
                
                result = service.spreadsheets().values().get(
                    spreadsheetId=sheet_id,
                    range=sheet_title
                ).execute()
                
                values = result.get('values', [])
                
                if values:
                    print_values(values)
                    
                    if output_file:
                        # Append to output file with sheet header
                        save_to_file(values, output_file, sheet_title=sheet_title)
                else:
                    print("No data found in this sheet.")
                print()
        
        return True
        
    except HttpError as e:
        print(f"❌ Error accessing spreadsheet: {e}")
        if e.status_code == 403:
            error_detail = json.loads(e.content.decode())
            if 'SERVICE_DISABLED' in str(error_detail):
                print("   ⚠️ Google Sheets API is not enabled for this project")
                print("   Enable it at: https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=667256544145")
        elif e.status_code == 404:
            print("   Spreadsheet not found. Check the spreadsheet ID")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_values(values, max_rows=100):
    """Print values in a readable format"""
    if not values:
        print("No data found.")
        return
    
    # Print column widths based on data
    num_cols = max(len(row) for row in values)
    col_widths = [0] * num_cols
    
    # Calculate column widths (limit to first 20 rows for efficiency)
    for row in values[:20]:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    col_widths = [min(w, 50) for w in col_widths]  # Cap at 50 chars
    
    # Print header separator
    separator = '+' + '+'.join('-' * (w + 2) for w in col_widths[:num_cols]) + '+'
    print(separator)
    
    # Print rows (limited to max_rows)
    for i, row in enumerate(values[:max_rows]):
        # Pad row to match column count
        padded_row = row + [''] * (num_cols - len(row))
        cells = [str(cell)[:col_widths[j]].ljust(col_widths[j]) for j, cell in enumerate(padded_row[:num_cols])]
        print('| ' + ' | '.join(cells) + ' |')
        
        # Print separator after header row (first row)
        if i == 0:
            print(separator)
    
    print(separator)
    
    if len(values) > max_rows:
        print(f"... ({len(values) - max_rows} more rows)")

def save_to_file(values, output_file, sheet_title=None):
    """Save values to a file (CSV format)"""
    mode = 'a' if sheet_title and os.path.exists(output_file) else 'w'
    
    with open(output_file, mode, newline='') as f:
        import csv
        writer = csv.writer(f)
        
        if sheet_title and mode == 'a':
            f.write(f"\n\n# Sheet: {sheet_title}\n")
        
        if values:
            writer.writerows(values)
    
    print(f"✓ Saved to: {output_file}")

def update_values(sheet_id, range_name, values, value_input_option='USER_ENTERED'):
    """Update values in a single range"""
    try:
        creds = get_credentials()
        if not creds:
            return False
        
        service = build('sheets', 'v4', credentials=creds)
        
        body = {
            'values': values
        }
        
        result = service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            body=body
        ).execute()
        
        print(f"✓ Updated {result.get('updatedCells', 0)} cells")
        print(f"  Range: {range_name}")
        return True
        
    except HttpError as e:
        print(f"❌ Error updating values: {e}")
        return False

def batch_update_values(sheet_id, data, value_input_option='USER_ENTERED'):
    """Update values in multiple ranges"""
    try:
        creds = get_credentials()
        if not creds:
            return False
        
        service = build('sheets', 'v4', credentials=creds)
        
        body = {
            'valueInputOption': value_input_option,
            'data': data
        }
        
        result = service.spreadsheets().values().batchUpdate(
            spreadsheetId=sheet_id,
            body=body
        ).execute()
        
        print(f"✓ Updated {result.get('totalUpdatedCells', 0)} cells total")
        for i, update_response in enumerate(result.get('responses', []), 1):
            print(f"  Range {i}: {update_response.get('updatedCells', 0)} cells")
        return True
        
    except HttpError as e:
        print(f"❌ Error batch updating values: {e}")
        return False

def append_values(sheet_id, range_name, values, value_input_option='USER_ENTERED'):
    """Append values to a sheet"""
    try:
        creds = get_credentials()
        if not creds:
            return False
        
        service = build('sheets', 'v4', credentials=creds)
        
        body = {
            'values': values
        }
        
        result = service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            body=body,
            insertDataOption='INSERT_ROWS'
        ).execute()
        
        updates = result.get('updates', {})
        print(f"✓ Appended {updates.get('updatedCells', 0)} cells")
        print(f"  Rows added: {updates.get('updatedRows', 0)}")
        print(f"  Table range: {updates.get('updatedRange', 'N/A')}")
        return True
        
    except HttpError as e:
        print(f"❌ Error appending values: {e}")
        return False

def clear_values(sheet_id, range_name):
    """Clear values from a range"""
    try:
        creds = get_credentials()
        if not creds:
            return False
        
        service = build('sheets', 'v4', credentials=creds)
        
        result = service.spreadsheets().values().clear(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()
        
        print(f"✓ Cleared range: {range_name}")
        return True
        
    except HttpError as e:
        print(f"❌ Error clearing values: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 google_sheets_api.py <command> [args...]")
        print("\nCommands:")
        print("  read <sheet_id> [range] [output_file]  - Read spreadsheet")
        print("  update <sheet_id> <range> <values...>  - Update values in range")
        print("  batch <sheet_id> <json_file>           - Batch update from JSON file")
        print("  append <sheet_id> <range> <values...>  - Append values to sheet")
        print("  clear <sheet_id> <range>                - Clear values from range")
        print("\nYour BOM sheet ID: 1MYNuzKqGEQszGO5iegXMWBzis7zdTSdvg4F3-kFWm-Q")
        print("\nExamples:")
        print("  # Read entire spreadsheet")
        print("  python3 google_sheets_api.py read 1MYNuzKqGEQszGO5iegXMWBzis7zdTSdvg4F3-kFWm-Q")
        print("  # Read specific range")
        print("  python3 google_sheets_api.py read 1MYNuzKqGEQszGO5iegXMWBzis7zdTSdvg4F3-kFWm-Q \"Sheet1!A1:Z100\"")
        print("  # Update a cell")
        print("  python3 google_sheets_api.py update 1MYNuzKqGEQszGO5iegXMWBzis7zdTSdvg4F3-kFWm-Q \"Sheet1!A1\" \"New Value\"")
        print("  # Update a row (comma-separated values)")
        print("  python3 google_sheets_api.py update 1MYNuzKqGEQszGO5iegXMWBzis7zdTSdvg4F3-kFWm-Q \"Sheet1!A2:C2\" \"Val1\" \"Val2\" \"Val3\"")
        print("  # Append a row")
        print("  python3 google_sheets_api.py append 1MYNuzKqGEQszGO5iegXMWBzis7zdTSdvg4F3-kFWm-Q \"Sheet1!A:A\" \"Item\" \"Description\" \"Qty\"")
        print("  # Clear a range")
        print("  python3 google_sheets_api.py clear 1MYNuzKqGEQszGO5iegXMWBzis7zdTSdvg4F3-kFWm-Q \"Sheet1!A2:Z100\"")
        print("  # Batch update from JSON")
        print("  python3 google_sheets_api.py batch 1MYNuzKqGEQszGO5iegXMWBzis7zdTSdvg4F3-kFWm-Q update.json")
        print("\nJSON file format for batch update:")
        print('  {"data": [{"range": "Sheet1!A1:B2", "values": [["Val1", "Val2"], ["Val3", "Val4"]]}]}')
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'read':
        if len(sys.argv) < 3:
            print("❌ Error: read command requires sheet_id")
            sys.exit(1)
        
        sheet_id = sys.argv[2]
        range_name = sys.argv[3] if len(sys.argv) > 3 else None
        output_file = sys.argv[4] if len(sys.argv) > 4 else None
        
        success = read_sheet(sheet_id, range_name, output_file)
    
    elif command == 'update':
        if len(sys.argv) < 5:
            print("❌ Error: update command requires sheet_id, range, and at least one value")
            print("  Usage: python3 google_sheets_api.py update <sheet_id> <range> <values...>")
            sys.exit(1)
        
        sheet_id = sys.argv[2]
        range_name = sys.argv[3]
        values_arg = sys.argv[4]
        
        # Parse values: can be "val1,val2" or separate args
        if ',' in values_arg or len(sys.argv) > 5:
            # Multiple values - parse as a row
            if len(sys.argv) > 5:
                # Values are separate arguments
                row_values = sys.argv[4:]
            else:
                # Parse comma-separated or pipe-separated values
                if '|' in values_arg:
                    row_values = [v.strip() for v in values_arg.split('|')]
                else:
                    row_values = [v.strip() for v in values_arg.split(',')]
            values = [row_values]
        else:
            # Single value
            values = [[values_arg]]
        
        success = update_values(sheet_id, range_name, values)
    
    elif command == 'batch':
        if len(sys.argv) < 4:
            print("❌ Error: batch command requires sheet_id and json_file")
            print("  Usage: python3 google_sheets_api.py batch <sheet_id> <json_file>")
            sys.exit(1)
        
        sheet_id = sys.argv[2]
        json_file = sys.argv[3]
        
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            success = batch_update_values(sheet_id, data.get('data', data))
        except FileNotFoundError:
            print(f"❌ Error: File not found: {json_file}")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"❌ Error: Invalid JSON in file: {json_file}")
            sys.exit(1)
    
    elif command == 'append':
        if len(sys.argv) < 5:
            print("❌ Error: append command requires sheet_id, range, and at least one value")
            print("  Usage: python3 google_sheets_api.py append <sheet_id> <range> <values...>")
            sys.exit(1)
        
        sheet_id = sys.argv[2]
        range_name = sys.argv[3]
        
        # Parse values similar to update
        if len(sys.argv) > 5:
            row_values = sys.argv[4:]
        else:
            values_arg = sys.argv[4]
            if '|' in values_arg:
                row_values = [v.strip() for v in values_arg.split('|')]
            else:
                row_values = [v.strip() for v in values_arg.split(',')]
        
        values = [row_values]
        success = append_values(sheet_id, range_name, values)
    
    elif command == 'clear':
        if len(sys.argv) < 4:
            print("❌ Error: clear command requires sheet_id and range")
            print("  Usage: python3 google_sheets_api.py clear <sheet_id> <range>")
            sys.exit(1)
        
        sheet_id = sys.argv[2]
        range_name = sys.argv[3]
        success = clear_values(sheet_id, range_name)
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
    
    sys.exit(0 if success else 1)
