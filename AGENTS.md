# Google Workspace API Tools

## Project Overview

This project provides command-line tools for interacting with Google Workspace APIs (Docs, Sheets, Gmail). All tools use OAuth2 authentication and share the same credentials file (`client_secrets.json` and `token.json`).

**Language:** Python 3
**Package Manager:** uv (preferred over pip)
**Virtual Environment:** `.venv/` (uv-managed)
**OAuth Project ID:** 667256544145

## Setup

```bash
# Install dependencies
uv sync

# Authenticate (run any command once)
./gdocs structure
```

To enable Gmail API (if needed):
https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=667256544145

## Architecture

### Package: `google_workspace_tools/`

The main Python package with centralized authentication:

| Module | Purpose |
|--------|---------|
| `auth.py` | OAuth2 credential management (single source of truth) |
| `cli.py` | Unified CLI entry point (`uv run gworkspace ...`) |
| `docs.py` | Google Docs operations |
| `sheets.py` | Google Sheets operations |
| `gmail.py` | Gmail operations |

### Wrappers

Bash wrappers for convenience with default document/sheet IDs:

| Wrapper | Default Target |
|---------|----------------|
| `./gdocs` | Doc: `1kJG9gFMy4M2iHfdxOhQ_KfNh1oy1P4aOdsDB-9626eg` |
| `./gsheets` | Sheet: `1MYNuzKqGEQszGO5iegXMWBzis7zdTSdvg4F3-kFWm-Q` |
| `./gmail` | Gmail inbox |

## Commands

### Google Docs

```bash
# View recent documents
uv run gworkspace docs recent 10

# Document structure
uv run gworkspace docs structure

# Text operations
uv run gworkspace docs append "Text"
uv run gworkspace docs insert "anchor" "new text"
uv run gworkspace docs replace "old" "new"
uv run gworkspace docs paragraph "New paragraph"
uv run gworkspace docs bold "text"

# Tabs
uv run gworkspace docs tabs list
uv run gworkspace docs tabs create "Tab Name"
uv run gworkspace docs tabs delete <tab_id>
uv run gworkspace docs tabs rename <tab_id> "New Name"

# Drive operations
uv run gworkspace docs copy <doc_id> "Copy Name"
uv run gworkspace docs rename <doc_id> "New Name"
uv run gworkspace docs move <doc_id> <folder_id>
uv run gworkspace docs delete <doc_id>

# Or use wrapper
./gdocs structure
./gdocs append "Text"
./gdocs open    # Open in browser
```

### Google Sheets

```bash
# Read
uv run gworkspace sheets read
uv run gworkspace sheets read "BOM!A1:Z100"

# Update
uv run gworkspace sheets update "BOM!A2" "Value"
uv run gworkspace sheets update "BOM!A2:D2" "A|B|C|D"

# Append
uv run gworkspace sheets append "BOM!A:A" "Item|Desc|100"

# Clear
uv run gworkspace sheets clear "BOM!A2:Z1000"

# Batch
uv run gworkspace sheets batch update.json

# Or use wrapper
./gsheets read
./gsheets update "BOM!A1" "Value"
./gsheets --id <custom_sheet_id> read   # Custom sheet
```

### Gmail

```bash
# List messages
uv run gworkspace gmail list 10
uv run gworkspace gmail list 50 'from:example.com'

# Get message
uv run gworkspace gmail get <message_id>
uv run gworkspace gmail body <message_id>

# Or use wrapper
./gmail list
./gmail get <message_id>
```

## Default Documents

| Name | Type | ID |
|------|------|-----|
| BOC Bootsklemme Pflichtenheft | Docs | `1kJG9gFMy4M2iHfdxOhQ_KfNh1oy1P4aOdsDB-9626eg` |
| BOM (Bill of Material for SY3) | Sheets | `1MYNuzKqGEQszGO5iegXMWBzis7zdTSdvg4F3-kFWm-Q` |
| Einkauf (Purchasing List) | Sheets | `1Y0jf1cACmYL1k56ow62vBP0hy1Nn32kyYFie9yZwj4M` |

Use custom sheet: `./gsheets --id <sheet_id> read`

## File Structure

```
.
├── AGENTS.md                    # This file
├── README.md                    # User documentation
├── pyproject.toml               # uv project configuration
├── client_secrets.json          # OAuth credentials (gitignored)
├── token.json                   # OAuth token (gitignored)
├── .venv/                       # uv-managed virtual environment
├── google_workspace_tools/      # Main Python package
│   ├── __init__.py
│   ├── auth.py
│   ├── cli.py
│   ├── docs.py
│   ├── sheets.py
│   └── gmail.py
├── tests/                       # Test files
├── gdocs                        # Bash wrapper for Docs
├── gsheets                      # Bash wrapper for Sheets
└── gmail                        # Bash wrapper for Gmail
```

## Dependencies

Managed via `pyproject.toml`:
- `google-api-python-client` - Google API client library
- `google-auth-httplib2` - Auth transport
- `google-auth-oauthlib` - OAuth library

## Troubleshooting

### Token Expired

```bash
rm -f token.json
./gdocs structure
```

### API Not Enabled

- **Docs:** https://console.developers.google.com/apis/api/docs.googleapis.com/overview?project=667256544145
- **Sheets:** https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=667256544145
- **Gmail:** https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=667256544145

### Scope Insufficient

```bash
rm -f token.json
# Re-authenticate
./gdocs structure
```
