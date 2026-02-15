#!/usr/bin/env python3
"""Upload a text file back to Google Doc"""

import os
import sys

def upload_to_google_doc(local_file, doc_id):
    """Upload content back to Google Doc - requires OAuth setup"""
    print("⚠ Full upload requires Google OAuth setup")
    print("\nFor now, here are your options:")
    print("1. Open your Google Doc in browser: https://docs.google.com/document/d/{doc_id}/edit")
    print(f"2. Paste the content from {local_file}")
    print("\nTo set up automated uploads, you need:")
    print("  - Google Cloud project with Google Docs API enabled")
    print("  - OAuth credentials (client_secrets.json)")
    print("  - google-api-python-client library")
    return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 upload_doc.py <local_file> <doc_id>")
        sys.exit(1)
    
    local_file = sys.argv[1]
    doc_id = sys.argv[2]
    
    upload_to_google_doc(local_file, doc_id)
