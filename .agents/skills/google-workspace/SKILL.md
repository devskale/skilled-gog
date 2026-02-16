---
name: google-workspace
description: Operate Google Docs, Google Sheets, and Gmail from this workspace using OAuth and uv. Use for reading/editing docs and sheets, and reading mail.
---

# Google Workspace Skill

This skill uses the `google_workspace_tools` Python package for Google Docs, Sheets, and Gmail operations.

## Installation

### Quick Install

```bash
curl -fsSL https://gworkspace.skale.dev/install.sh | bash
```

Or directly from GitHub:

```bash
curl -fsSL https://raw.githubusercontent.com/devskale/skilled-gog/main/install.sh | bash
```

### Manual Install

```bash
# Clone and enter
git clone https://github.com/devskale/skilled-gog.git ~/.gworkspace
cd ~/.gworkspace

# Install dependencies
uv sync

# Run
uv run gworkspace docs recent 10
```

### Credentials Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials?project=667256544145)
2. Create OAuth 2.0 credentials (Desktop application)
3. Download JSON and save as `~/.gworkspace/client_secrets.json`
4. Run any command to authenticate

## Commands

### Docs

```bash
# View recent documents
gworkspace docs recent 10

# Document structure
gworkspace docs structure

# Text operations
gworkspace docs append "Text"
gworkspace docs insert "anchor" "new text"
gworkspace docs replace "old" "new"
gworkspace docs paragraph "Heading"
gworkspace docs bold "Important"

# Tabs
gworkspace docs tabs list
gworkspace docs tabs create "New Tab"
gworkspace docs tabs delete <tab_id>
gworkspace docs tabs rename <id> "Name"

# Drive (document management)
gworkspace docs copy <doc_id> [name]
gworkspace docs rename <doc_id> <name>
gworkspace docs move <doc_id> <folder_id>
gworkspace docs delete <doc_id>
```

### Sheets

```bash
gworkspace sheets read
gworkspace sheets read "BOM!A1:Z100"
gworkspace sheets update "BOM!A2:D2" "A|B|C|D"
gworkspace sheets append "BOM!A:A" "Item|Description|100"
gworkspace sheets clear "BOM!A2:Z1000"
gworkspace sheets batch update.json
```

### Gmail

```bash
gworkspace gmail list 10
gworkspace gmail get <message_id>
gworkspace gmail body <message_id>
```

## Google Docs Tabs

Google Docs supports tabs (like sheets in Google Sheets):

```bash
# List all tabs
gworkspace docs tabs list

# Create a child tab
gworkspace docs tabs create "Child" --parent <parent_tab_id>

# Work with specific tab
gworkspace docs append "Text" --tab t.abc123
gworkspace docs replace "old" "new" --tab t.abc123
```

## Default Documents

| Name | Type | ID |
|------|------|-----|
| BOC Bootsklemme Pflichtenheft | Docs | `1kJG9gFMy4M2iHfdxOhQ_KfNh1oy1P4aOdsDB-9626eg` |
| BOM (Bill of Material for SY3) | Sheets | `1MYNuzKqGEQszGO5iegXMWBzis7zdTSdvg4F3-kFWm-Q` |

## Troubleshooting

### Re-authenticate

```bash
rm -f ~/.gworkspace/token.json
gworkspace docs recent 1
```

### Enable APIs

- **Docs:** https://console.developers.google.com/apis/api/docs.googleapis.com/overview?project=667256544145
- **Sheets:** https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=667256544145
- **Gmail:** https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=667256544145

## Project Structure

```
~/.gworkspace/
├── google_workspace_tools/   # Python package
│   ├── auth.py               # Centralized OAuth
│   ├── cli.py                # CLI entry point
│   ├── docs.py
│   ├── sheets.py
│   └── gmail.py
├── client_secrets.json       # Your OAuth credentials
├── token.json                # Auto-generated token
└── install.sh                # Install script
```
