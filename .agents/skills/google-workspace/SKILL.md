---
name: google-workspace
description: Operate Google Docs, Google Sheets, and Gmail from this workspace using OAuth and uv. Use for reading/editing docs and sheets, and reading mail.
---

# Google Workspace Skill

Use this skill with the project at:

`/Users/johannwaldherr/code/google`

This skill is paired with the local Python project and wrappers:
- `uv run gworkspace ...`
- `./gdocs ...`
- `./gsheets ...`
- `./gmail ...`

## New: Google Docs Tabs Support

Google Docs now supports tabs (like sheets in Google Sheets). Each document can have multiple tabs with their own content, and tabs can be nested (child tabs).

**Key Concepts:**
- Each tab has a unique `tabId` and `title`
- Tab content is accessed via `document.tabs[].documentTab.body`
- Without tabs support, only the first tab is accessible
- Most operations can target a specific tab using `--tab <tab_id>`

## Preconditions

1. `uv` installed
2. `client_secrets.json` present in project root
3. APIs enabled in Google Cloud project:
- Docs API
- Sheets API
- Gmail API (if Gmail commands are used)

## One-Time Setup

```bash
cd /Users/johannwaldherr/code/google
uv sync
```

Authenticate by running any command once:

```bash
./gdocs structure
```

## Commands

### Unified CLI (preferred)

```bash
# Docs
uv run gworkspace docs recent 10
uv run gworkspace docs structure
uv run gworkspace docs structure --tabs          # Show all tabs structure
uv run gworkspace docs append "Text"
uv run gworkspace docs append "Text" --tab <id>  # Append to specific tab
uv run gworkspace docs insert "anchor" "new text"
uv run gworkspace docs replace "old" "new"
uv run gworkspace docs paragraph "Heading"
uv run gworkspace docs bold "Important"

# Tabs Commands
uv run gworkspace docs tabs list                 # List all tabs
uv run gworkspace docs tabs create "New Tab"     # Create new tab
uv run gworkspace docs tabs delete <tab_id>      # Delete tab
uv run gworkspace docs tabs rename <id> "Name"   # Rename tab

# Drive Commands (document management)
uv run gworkspace docs copy <doc_id> [name]      # Copy document (WORK-Kopie)
uv run gworkspace docs rename <doc_id> <name>    # Rename document
uv run gworkspace docs move <doc_id> <folder_id> # Move to folder
uv run gworkspace docs delete <doc_id>           # Move to trash

# Sheets
uv run gworkspace sheets read
uv run gworkspace sheets read "BOM!A1:Z100"
uv run gworkspace sheets update "BOM!A2:D2" "A|B|C|D"
uv run gworkspace sheets append "BOM!A:A" "Item|Description|100"
uv run gworkspace sheets clear "BOM!A2:Z1000"
uv run gworkspace sheets batch update.json

# Gmail
uv run gworkspace gmail list 10
uv run gworkspace gmail get <message_id>
uv run gworkspace gmail body <message_id>
```

### Wrappers (same behavior)

```bash
./gdocs recent 10
./gdocs structure
./gdocs copy <doc_id> "New Name"      # Copy document
./gdocs rename <doc_id> "New Name"    # Rename document
./gdocs move <doc_id> <folder_id>     # Move to folder
./gdocs delete <doc_id>               # Move to trash
./gsheets read
./gmail list
```

Use custom sheet id with wrapper:

```bash
./gsheets --id <sheet_id> read "Sheet1!A1:C20"
```

## Defaults

- Default document id: `1kJG9gFMy4M2iHfdxOhQ_KfNh1oy1P4aOdsDB-9626eg`
- Default sheet id: `1MYNuzKqGEQszGO5iegXMWBzis7zdTSdvg4F3-kFWm-Q`

## Working with Tabs

Google Docs tabs allow you to organize content within a single document, similar to sheets in Google Sheets.

### List Tabs

```bash
# List all tabs in the document
uv run gworkspace docs tabs list

# Example output:
# Tab ID           | Title           | Type
# -----------------|-----------------|--------
# t.abc123         | Tab 1           | documentTab
# t.def456         | Tab 2           | documentTab
# t.ghi789         | Notes           | documentTab (child of Tab 2)
```

### Create Tabs

```bash
# Create a new tab at the end
uv run gworkspace docs tabs create "New Tab Name"

# Create a child tab (nested under another tab)
uv run gworkspace docs tabs create "Child Tab" --parent <parent_tab_id>

# Create tab at specific index
uv run gworkspace docs tabs create "Tab Name" --index 0
```

### Work with Specific Tabs

```bash
# Append text to a specific tab
uv run gworkspace docs append "Text content" --tab t.abc123

# Insert text in specific tab
uv run gworkspace docs insert "anchor" "new text" --tab t.abc123

# Replace text in specific tab (defaults to all tabs if not specified)
uv run gworkspace docs replace "old" "new" --tab t.abc123

# Show structure of specific tab
uv run gworkspace docs structure --tab t.abc123
```

### Manage Tabs

```bash
# Rename a tab
uv run gworkspace docs tabs rename t.abc123 "New Tab Name"

# Delete a tab (and all its content)
uv run gworkspace docs tabs delete t.abc123

# Update tab properties
uv run gworkspace docs tabs update t.abc123 --index 0  # Move to first position
```

### Wrapper Commands (Tabs)

```bash
./gdocs tabs list
./gdocs tabs create "New Tab"
./gdocs tabs delete <tab_id>
./gdocs tabs rename <tab_id> "New Name"
./gdocs structure --tabs              # Show all tabs
./gdocs append "Text" --tab <tab_id>  # Append to specific tab
```

## Drive Commands (Document Management)

```bash
# Copy document (default: original + " - WORK-Kopie")
./gdocs copy <doc_id>
./gdocs copy <doc_id> "Custom Name"

# Rename document
./gdocs rename <doc_id> "New Name"

# Move document to folder
./gdocs move <doc_id> <folder_id>

# Delete document (move to trash - restore via Google Drive)
./gdocs delete <doc_id>
```

Requires Drive API scope (included in SCOPES).

## Troubleshooting

Re-authenticate if scopes changed:

```bash
cd /Users/johannwaldherr/code/google
rm -f token.json
./gdocs structure
```

If Gmail fails with API disabled, enable:

https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=667256544145

## Notes

- `token.json` and `client_secrets.json` are local secret files.
- The project uses `uv`; avoid `pip`/`python` direct workflows.
