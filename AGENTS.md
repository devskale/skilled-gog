# Google Workspace API Tools

## Project Overview

This project provides command-line tools for interacting with Google Workspace APIs (Docs, Sheets, Gmail). All tools use OAuth2 authentication and share the same credentials file (`client_secrets.json` and `token.json`).

**Language:** Python 3
**Package Manager:** uv (preferred over pip)
**Virtual Environment:** `.venv/` (uv-managed)
**OAuth Project ID:** 667256544145

## Setup

```bash
# Already configured:
# - Google Cloud project created
# - Google Docs API enabled
# - Google Sheets API enabled
# - OAuth credentials (client_secrets.json)
# - uv package manager configured
# - pyproject.toml with dependencies defined

# To install/update dependencies:
uv sync

# To enable Gmail API (if needed):
# Visit: https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=667256544145

# IMPORTANT: Always use uv over python or pip
# uv is faster and manages dependencies more efficiently
```

## Package Management: Use uv

**Always use `uv` instead of `python` or `pip`** for better performance and dependency management.

**Project Setup:**
- `pyproject.toml` - Defines project and dependencies
- `.venv/` - uv-managed virtual environment (auto-created)
- Use `uv sync` to install/update dependencies

**Running Python scripts with uv:**
```bash
# Preferred: Use bash wrappers (they use uv internally)
./gsheets read
./gdocs structure
./gmail list

# Or use uv run directly
uv run google_gmail_api.py list
uv run google_sheets_api.py read <sheet_id>
uv run google_docs_api.py download <doc_id>
```

**Installing dependencies:**
```bash
# Install all dependencies from pyproject.toml
uv sync

# Add new dependency
uv add <package>

# Example: Add requests library
uv add requests
```

**Why uv?**
- Faster than pip (uses Rust internally)
- Better dependency resolution
- Handles virtual environments automatically
- Consistent across all commands
- Lock file for reproducible builds

## Tools

### 1. Google Docs (`gdocs`, `gdocs_edit.py`)

**Purpose:** Read and edit Google Docs directly via API

**Commands:**
```bash
./gdocs structure              # Show document structure
./gdocs paragraph "text"       # Add paragraph
./gdocs append "text"          # Append text
./gdocs replace "old" "new"   # Replace text
./gdocs insert "anchor" "new"  # Insert after anchor
./gdocs bold "text"           # Make text bold
./gdocs open                  # Open in browser
```

**Current Document:** BOC Bootsklemme Pflichtenheft
- **ID:** `1kJG9gFMy4M2iHfdxOhQ_KfNh1oy1P4aOdsDB-9626eg`
- **Link:** https://docs.google.com/document/d/1kJG9gFMy4M2iHfdxOhQ_KfNh1oy1P4aOdsDB-9626eg/edit

**Python Script:**
```bash
# Preferred: Use uv
uv run gdocs_edit.py <command> <doc_id> [args...]

# Or use bash wrapper
./gdocs <command> [args...]
```

### 2. Google Sheets (`gsheets`, `google_sheets_api.py`)

**Purpose:** Read and edit Google Sheets directly via API

**Commands:**
```bash
./gsheets read [range]           # Read spreadsheet
./gsheets update <range> <vals>  # Update cells
./gsheets append <range> <vals>   # Append row
./gsheets clear <range>           # Clear range
./gsheets batch <json_file>       # Batch update
./gsheets open                   # Open in browser
```

**Current Spreadsheet:** BOM (Bill of Material for SY3)
- **ID:** `1MYNuzKqGEQszGO5iegXMWBzis7zdTSdvg4F3-kFWm-Q`
- **Link:** https://docs.google.com/spreadsheets/d/1MYNuzKqGEQszGO5iegXMWBzis7zdTSdvg4F3-kFWm-Q/edit
- **Sheets:**
  - `BOM` (ID: 1596294757) - Main bill of materials
  - `Lieferant` (ID: 1727136135) - Supplier information

**Python Script:**
```bash
# Preferred: Use uv
uv run google_sheets_api.py <command> <sheet_id> [args...]

# Or use bash wrapper
./gsheets <command> [args...]
```

**Example Usage:**
```bash
# Read entire sheet
./gsheets read

# Read specific range
./gsheets read "BOM!A1:Z100"

# Update a cell
./gsheets update "BOM!A2" "New Value"

# Update a row (pipe-separated values)
./gsheets update "BOM!A2:D2" "Val1|Val2|Val3|Val4"

# Append a row
./gsheets append "BOM!A:A" "New Item|Description|100"

# Clear a range
./gsheets clear "BOM!A2:Z1000"
```

### 3. Gmail (`gmail`, `google_gmail_api.py`)

**Purpose:** Read Gmail messages via API

**Status:** Script and wrapper created, Gmail API not yet enabled

**Commands:**
```bash
./gmail list [max] [query] [labels]  # List messages
./gmail get <message_id>            # Get full message
./gmail body <message_id>            # Get message body only
./gmail open                       # Open Gmail in browser
```

**Python Script:**
```bash
# Preferred: Use uv
uv run google_gmail_api.py <command> [args...]

# Or use bash wrapper
./gmail <command> [args...]
```

**Example Usage:**
```bash
# List 10 most recent messages
./gmail list

# List 20 messages
./gmail list 20

# List messages from specific sender
./gmail list 50 'from:example.com'

# List messages with label
./gmail list 50 '' 'INBOX'

# Get specific message
./gmail get 123456789abcdef

# Get message body only
./gmail body 123456789abcdef
```

**To Enable Gmail API:**
Visit: https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=667256544145

## Development Notes

### Authentication

All tools share OAuth2 credentials:
- **Credentials File:** `client_secrets.json`
- **Token File:** `token.json`
- **Scopes:**
  - Docs: `https://www.googleapis.com/auth/documents`, `https://www.googleapis.com/auth/drive`
  - Sheets: `https://www.googleapis.com/auth/spreadsheets`, `https://www.googleapis.com/auth/drive`
  - Gmail: `https://www.googleapis.com/auth/gmail.readonly`, `https://www.googleapis.com/auth/drive`

If token expires or scopes change, delete `token.json` and re-authenticate.

### File Structure

```
.
├── AGENTS.md                    # This file
├── README.md                    # User documentation
├── doclinks.md                  # Document links and IDs
├── pyproject.toml               # uv project configuration
├── client_secrets.json          # OAuth credentials (not in git)
├── token.json                  # OAuth token (not in git, auto-generated)
├── .venv/                     # uv-managed virtual environment
├── google_docs_env/            # Legacy venv (can be removed)
├── gdocs                      # Bash wrapper for Docs API
├── gdocs_edit.py              # Google Docs API Python script
├── google_docs_api.py         # Docs download/upload script
├── gsheets                    # Bash wrapper for Sheets API
├── google_sheets_api.py       # Google Sheets API Python script
├── gmail                      # Bash wrapper for Gmail API
└── google_gmail_api.py        # Gmail API Python script
```

### Dependencies

All Python scripts use common dependencies:
- `google-api-python-client` - Google API client library
- `google-auth-httplib2` - Auth transport
- `google-auth-oauthlib` - OAuth library

**Dependencies are managed via uv in `pyproject.toml`.**

## Troubleshooting

### API Not Enabled

If you get an error saying an API is not enabled:
- **Docs:** https://console.developers.google.com/apis/api/docs.googleapis.com/overview?project=667256544145
- **Sheets:** https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=667256544145
- **Gmail:** https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=667256544145

### Token Expired

If authentication fails:
```bash
rm -f token.json
# Run any command - will prompt for re-authentication
./gdocs structure
```

### Scope Insufficient

If you get "insufficient authentication scopes":
```bash
rm -f token.json
# Re-authenticate to get new scopes
./gsheets read
```

## Current Status

| Service | API Enabled | Python Script | Bash Wrapper | Working |
|---------|-------------|---------------|---------------|----------|
| Docs    | ✅ Yes      | ✅            | ✅            | ✅       |
| Sheets  | ✅ Yes      | ✅            | ✅            | ✅       |
| Gmail   | ❌ No       | ✅            | ✅            | ⏳       |

## Testing

**Safe Testing Guidelines:**
- Always test on empty cells or test data first
- Verify changes by reading back before/after
- Use `open` command to visually verify in browser
- Document tests in comments or TODOs

**Example Safe Test:**
```bash
# 1. Find empty area
./gsheets read "Sheet1!A10:F10"

# 2. Update empty cell with test value
./gsheets update "Sheet1!A10" "TEST_CELL_001"

# 3. Read back to verify
./gsheets read "Sheet1!A10"

# 4. Open in browser to visually verify
./gsheets open

# 5. Clean up if needed
./gsheets update "Sheet1!A10" ""
```

## Next Steps

1. ✅ Enable Gmail API (when needed)
2. ✅ Test Gmail reader functionality
3. ⏳ Add more advanced Docs editing (tables, images, formatting)
4. ⏳ Add Sheets batch operations UI helper
5. ⏳ Create unified CLI tool combining all services
6. ⏳ Remove legacy `google_docs_env/` after confirming `.venv/` works
