# Google Workspace Tools

A Python CLI for Google Workspace automation (Docs, Sheets, Gmail) with unified OAuth2 authentication.

## Install

```bash
curl -fsSL https://skale.dev/skilled-google/install.sh | bash
```

Install paths:
- Tools: `~/.gworkspace`
- CLI wrappers: `~/.local/bin` (`gworkspace`, `gdocs`, `gsheets`, `gmail`)

## Credentials Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 credentials (Desktop application)
3. Download JSON and save as `~/.gworkspace/client_secrets.json`
4. Run any command to authenticate

## Usage

### Google Docs

```bash
# List recent documents
gworkspace docs recent 10

# View document structure
gworkspace docs structure

# Download as Markdown (recommended for edits)
gworkspace docs --doc-id "<doc_id>" download ./mydoc 1.0
# Creates: ./mydoc/doc.md + ./mydoc/img/

# Upload edited Markdown as new version
gworkspace docs upload ./mydoc/doc.md 1.2

# Quick text operations
gworkspace docs append "New paragraph"
gworkspace docs insert "anchor" "text to insert"
gworkspace docs replace "old text" "new text"
gworkspace docs paragraph "Heading Text"
gworkspace docs bold "text to bold"

# Tabs
gworkspace docs tabs list
gworkspace docs tabs create "New Tab"
gworkspace docs tabs delete <tab_id>
```

### Google Sheets

```bash
# Read entire sheet or range
gworkspace sheets read
gworkspace sheets read "Sheet1!A1:Z100"

# Update cells (pipe-separated values)
gworkspace sheets update "Sheet1!A2:D2" "Val1|Val2|Val3|Val4"

# Append row
gworkspace sheets append "Sheet1!A:A" "Item|Description|100"

# Clear range
gworkspace sheets clear "Sheet1!A2:Z1000"

# Batch update from JSON
gworkspace sheets batch updates.json
```

### Gmail

```bash
# List messages
gworkspace gmail list 10
gworkspace gmail list 20 "from:example.com"
gworkspace gmail list 50 "subject:invoice"

# Get message details
gworkspace gmail get <message_id>
gworkspace gmail body <message_id>

# Create draft
gworkspace gmail draft "to@example.com" "Subject" "Email body text"

# Send (requires approval flag)
gworkspace gmail send --approve-send "to@example.com" "Subject" "Email body"
```

### Wrappers (with default IDs)

```bash
./gdocs structure
./gdocs append "Text"

./gsheets read
./gsheets update "BOM!A1" "Value"

./gmail list 10
./gmail draft "to@example.com" "Subject" "Body"
```

## Markdown Workflow (Docs)

For large document edits, use the download/edit/upload workflow:

```bash
# 1. Download
gworkspace docs --doc-id "1kJG9gFMy4M2iHfdxOhQ_KfNh1oy1P4aOdsDB-9626eg" download ./boc-doc 1.0

# 2. Edit locally
vim ./boc-doc/doc.md

# 3. Upload as new version
gworkspace docs upload ./boc-doc/doc.md 1.1
```

Note: Tabbed docs are flattened on download (tab boundaries become `#` headings).

## Update

```bash
cd ~/.gworkspace && git pull && uv sync
```

## AI Agent Skill

For AI agents (pi, Claude, etc.), install the skill:

```bash
curl -fsSL https://skale.dev/install-gog-skill.sh | bash
```

Then link in your project:

```bash
ln -s ~/.pi/agent/skills/google-workspace .agents/skills/google-workspace
```

## Local Development

```bash
git clone https://github.com/devskale/skilled-gog.git
cd skilled-gog
uv sync

uv run gworkspace docs structure
./gdocs structure
```

## Run Tests

```bash
uv run pytest
```

## License

MIT
