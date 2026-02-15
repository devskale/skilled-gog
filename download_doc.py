#!/usr/bin/env python3
"""Download a Google Doc by ID using Google API"""

import os
import sys

def download_google_doc(doc_id, output_file):
    """Download a Google Doc as text"""
    try:
        # Try using requests with Google Docs export URL
        import requests
        
        url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
        
        # Note: This requires the doc to be publicly accessible or you need OAuth
        response = requests.get(url)
        
        if response.status_code == 200:
            with open(output_file, 'w') as f:
                f.write(response.text)
            print(f"✓ Downloaded to {output_file}")
            return True
        else:
            print(f"✗ Failed to download: {response.status_code}")
            print("The document may not be publicly accessible")
            return False
            
    except ImportError:
        print("✗ requests library not installed")
        print("Install with: pip3 install requests")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 download_doc.py <doc_id> <output_file>")
        print("\nYour doc ID: 1kJG9gFMy4M2iHfdxOhQ_KfNh1oy1P4aOdsDB-9626eg")
        sys.exit(1)
    
    doc_id = sys.argv[1]
    output_file = sys.argv[2]
    
    success = download_google_doc(doc_id, output_file)
    sys.exit(0 if success else 1)
