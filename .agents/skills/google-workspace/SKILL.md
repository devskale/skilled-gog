---
name: google-workspace
description: Operate Google Docs, Google Sheets, and Gmail from this workspace using OAuth and uv. Use for reading/editing docs and sheets, and reading/drafting/sending mail.
---

# Google Workspace Skill

This skill uses the `google_workspace_tools` Python package for Google Docs, Sheets, and Gmail operations.

## Installation

### Quick Install

```bash
curl -fsSL https://skale.dev/skilled-google/install.sh | bash
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

Authenticate by running a command for each service you use:

```bash
./gdocs structure
./gsheets read
./gmail list 1
```

Important:
- This project uses one shared `token.json`.
- Docs, Sheets, and Gmail require different OAuth scopes.
- If you switch services and see `insufficient authentication scopes` or `invalid_scope`, re-authenticate:

```bash
cd ~/.gworkspace
rm -f token.json
# then run the service command again, e.g.
./gmail list 1
```

## Commands

### Docs

```bash
# View recent documents
gworkspace docs recent 10

# Markdown workflow (recommended for large rewrites)
gworkspace docs --doc-id "<doc_id>" download "/tmp/gdoc_export_test" 1.0
gworkspace docs upload "/tmp/gdoc_export_test/doc.md" 1.2

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
gworkspace gmail list 20 "from:wibke"
gworkspace gmail get <message_id>
gworkspace gmail body <message_id>
gworkspace gmail draft "alice@example.com" "Subject" "Body text"
gworkspace gmail send --approve-send "alice@example.com" "Subject" "Body text"
```

### Wrappers (same behavior)

```bash
./gdocs recent 10
./gdocs download "/tmp/gdoc_export_test" 1.0
./gdocs upload "/tmp/gdoc_export_test/doc.md" 1.2
./gdocs structure
./gsheets read
./gmail list
./gmail list 20 "from:wibke"
./gmail draft "alice@example.com" "Subject" "Body text"
./gmail send --approve-send "alice@example.com" "Subject" "Body text"
```

## Markdown Download (Docs)

Use this for extensive edits instead of many API mutations.

### Export

```bash
gworkspace docs --doc-id "<doc_id>" download "/tmp/gdoc_export_test" 1.0
```

What export does:
- Downloads as Markdown
- Merges all tabs recursively into one `doc.md`
- Converts every tab boundary to a top-level `#` heading in `doc.md`
- Adds YAML frontmatter (`doc_id`, `doc_url`, `drive_parent_id`, `version`, etc.)
- Stores images in relative `img/`

Output structure:

```text
/tmp/gdoc_export_test/
  doc.md
  img/
    image1.png
    image2.png
```

### Verify Export

```bash
sed -n '1,30p' /tmp/gdoc_export_test/doc.md
rg -n "^# " /tmp/gdoc_export_test/doc.md
ls -la /tmp/gdoc_export_test/img
```

### Local Edit + Upload New Version

```bash
# edit /tmp/gdoc_export_test/doc.md locally
gworkspace docs upload "/tmp/gdoc_export_test/doc.md" 1.2
```

Import behavior:
- Creates new doc `filename_V1.2`
- Writes metadata to Drive `appProperties`
- Adds visible import header in the doc for human traceability
- Upload does not recreate Google Docs tabs (single-body doc upload)

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
├── email_footer.md           # Customizable AI email footer
└── install.sh                # Install script
```

## Notes

- `token.json` and `client_secrets.json` are local secret files.
- The project uses `uv`; avoid `pip`/`python` direct workflows.
- AI-created emails (draft/send) always append footer from `email_footer.md`.
- Edit `email_footer.md` to customize the footer (default: `gesendet von KI, iA`).
- Sending policy: use `send` only after explicit user approval; command requires `--approve-send`.
