# Google Workspace Tools

A Python CLI for Google Workspace automation (Docs, Sheets, Gmail) with unified OAuth2 authentication.

## Quick Install

```bash
curl -fsSL https://skale.dev/skilled-google/install.sh | bash
```

Or directly from GitHub:

```bash
curl -fsSL https://raw.githubusercontent.com/devskale/skilled-gog/main/install.sh | bash
```

Default install paths:
- Project checkout: `~/.gworkspace`
- CLI wrappers: `~/.local/bin` (`gworkspace`, `gdocs`, `gsheets`, `gmail`)

Verify installation:

```bash
which gworkspace
gworkspace --version
```

## Features

- **Google Docs**: `recent`, `export-md`, `import-md`, `structure`, `append`, `insert`, `replace`, `paragraph`, `bold`, `tabs`
- **Google Sheets**: `read`, `update`, `append`, `clear`, `batch`
- **Gmail**: `list`, `get`, `body`, `draft`, `send`
- Shared OAuth2 credential flow across all services

## Usage

### Unified CLI

```bash
# Docs
gworkspace docs recent 10
gworkspace docs structure
gworkspace docs append "Hello"
gworkspace docs export-md ./docs/mydoc 1.0
gworkspace docs import-md ./docs/mydoc/doc.md 1.2

# Sheets
gworkspace sheets read
gworkspace sheets update "BOM!A2:D2" "Val1|Val2|Val3|Val4"

# Gmail
gworkspace gmail list 10
gworkspace gmail draft "user@example.com" "Subject" "Message body"
gworkspace gmail send --approve-send "user@example.com" "Subject" "Message body"
```

### Local Development

```bash
# Clone and install
git clone https://github.com/devskale/skilled-gog.git
cd skilled-gog
uv sync

# Run locally
uv run gworkspace docs structure

# Or use wrappers with default IDs
./gdocs structure
./gsheets read
./gmail list 20
```

## Credentials Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials?project=667256544145)
2. Create OAuth 2.0 credentials (Desktop application)
3. Download JSON and save as `client_secrets.json`
4. Run any command to authenticate

## Project Layout

```
google_workspace_tools/   # Python package
├── auth.py               # Centralized OAuth
├── cli.py                # CLI entry point
├── docs.py               # Docs operations
├── sheets.py             # Sheets operations
└── gmail.py              # Gmail operations

tests/                    # Unit tests
gdocs, gsheets, gmail     # Local wrappers
install.sh                # Install script
```

## Run Tests

```bash
uv run pytest
```

## License

MIT
