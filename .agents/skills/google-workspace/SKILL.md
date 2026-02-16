---
name: google-workspace
description: Operate Google Docs, Google Sheets, and Gmail from this workspace using OAuth and uv. Use for reading/editing docs and sheets, and reading mail.
---

# Google Workspace Skill

This skill uses the `google_workspace_tools` Python package in this project.

**Commands:**
- `uv run gworkspace docs ...`
- `uv run gworkspace sheets ...`
- `uv run gworkspace gmail ...`

**Convenience wrappers:**
- `./gdocs ...` (uses default doc ID)
- `./gsheets ...` (uses default sheet ID)
- `./gmail ...`

## Google Docs Tabs Support

Google Docs supports tabs (like sheets in Google Sheets). Each document can have multiple tabs with their own content, and tabs can be nested.

**Key Concepts:**
- Each tab has a unique `tabId` and `title`
- Tab content is accessed via `document.tabs[].documentTab.body`
- Most operations can target a specific tab using `--tab <tab_id>`

## Preconditions

1. `uv` installed
2. `client_secrets.json` present in project root
3. APIs enabled in Google Cloud project (ID: 667256544145):
   - Docs API
   - Sheets API
   - Gmail API (if Gmail commands are used)

## One-Time Setup

```bash
uv sync
```

Authenticate by running any command once:

```bash
./gdocs structure
```

## Commands

### Docs

```bash
# View recent documents
uv run gworkspace docs recent 10

# Document structure
uv run gworkspace docs structure
uv run gworkspace docs structure --tabs          # Show all tabs structure

# Text operations
uv run gworkspace docs append "Text"
uv run gworkspace docs append "Text" --tab <id>  # Append to specific tab
uv run gworkspace docs insert "anchor" "new text"
uv run gworkspace docs replace "old" "new"
uv run gworkspace docs paragraph "Heading"
uv run gworkspace docs bold "Important"

# Tabs
uv run gworkspace docs tabs list                 # List all tabs
uv run gworkspace docs tabs create "New Tab"     # Create new tab
uv run gworkspace docs tabs delete <tab_id>      # Delete tab
uv run gworkspace docs tabs rename <id> "Name"   # Rename tab

# Drive (document management)
uv run gworkspace docs copy <doc_id> [name]      # Copy document
uv run gworkspace docs rename <doc_id> <name>    # Rename document
uv run gworkspace docs move <doc_id> <folder_id> # Move to folder
uv run gworkspace docs delete <doc_id>           # Move to trash
```

### Sheets

```bash
uv run gworkspace sheets read
uv run gworkspace sheets read "BOM!A1:Z100"
uv run gworkspace sheets update "BOM!A2:D2" "A|B|C|D"
uv run gworkspace sheets append "BOM!A:A" "Item|Description|100"
uv run gworkspace sheets clear "BOM!A2:Z1000"
uv run gworkspace sheets batch update.json
```

### Gmail

```bash
uv run gworkspace gmail list 10
uv run gworkspace gmail get <message_id>
uv run gworkspace gmail body <message_id>
```

### Wrappers (same behavior, use defaults)

```bash
./gdocs recent 10
./gdocs structure
./gdocs append "Text"
./gsheets read
./gsheets update "Sheet1!A1" "Value"
./gmail list
```

Use custom sheet ID with wrapper:

```bash
./gsheets --id <sheet_id> read "Sheet1!A1:C20"
```

## Defaults

- Default document ID: `1kJG9gFMy4M2iHfdxOhQ_KfNh1oy1P4aOdsDB-9626eg`
- Default sheet ID: `1MYNuzKqGEQszGO5iegXMWBzis7zdTSdvg4F3-kFWm-Q`

## Working with Tabs

```bash
# List all tabs
uv run gworkspace docs tabs list

# Create a child tab (nested)
uv run gworkspace docs tabs create "Child Tab" --parent <parent_tab_id>

# Work with specific tab
uv run gworkspace docs append "Text" --tab t.abc123
uv run gworkspace docs replace "old" "new" --tab t.abc123

# Manage tabs
./gdocs tabs list
./gdocs tabs create "New Tab"
./gdocs tabs delete <tab_id>
./gdocs tabs rename <tab_id> "New Name"
```

## Troubleshooting

Re-authenticate if scopes changed:

```bash
rm -f token.json
./gdocs structure
```

If Gmail fails with API disabled, enable:

https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=667256544145

## Project Structure

```
.
├── google_workspace_tools/     # Main Python package
│   ├── __init__.py
│   ├── auth.py                 # Centralized OAuth
│   ├── cli.py                  # Unified CLI entry point
│   ├── docs.py                 # Docs operations
│   ├── sheets.py               # Sheets operations
│   └── gmail.py                # Gmail operations
├── tests/                      # Test files
├── gdocs                       # Docs wrapper
├── gsheets                     # Sheets wrapper
├── gmail                       # Gmail wrapper
├── pyproject.toml              # Package config
├── client_secrets.json         # OAuth credentials (gitignored)
└── token.json                  # OAuth token (gitignored)
```

## Notes

- `token.json` and `client_secrets.json` are local secret files (gitignored)
- Uses `uv` for dependency management - do not use `pip` directly
