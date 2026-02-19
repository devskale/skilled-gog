---
name: google-workspace
description: Operate Google Docs, Google Sheets, and Gmail from this workspace using OAuth and uv. Use for reading/editing docs and sheets, and reading/drafting/sending mail.
---

# Google Workspace Skill

This skill provides access to Google Docs, Sheets, and Gmail operations.

## Installation

### Install from GitHub

```bash
curl -fsSL https://skale.dev/skilled-google/install.sh | bash
```

Or manually:

```bash
git clone https://github.com/devskale/skilled-gog.git ~/.gworkspace
cd ~/.gworkspace && uv sync
```

### Update

Pull latest changes from GitHub:

```bash
cd ~/.gworkspace && git pull && uv sync
```

### Verify Installation

```bash
ls ~/.gworkspace/google_workspace_tools/
ls ~/.gworkspace/client_secrets.json
```

### Credentials Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials?project=667256544145)
2. Create OAuth 2.0 credentials (Desktop application)
3. Download JSON and save as `~/.gworkspace/client_secrets.json`
4. Run any command to authenticate

## Commands

All commands are run from `~/.gworkspace`:

### Docs

```bash
cd ~/.gworkspace && uv run gworkspace docs recent 10
cd ~/.gworkspace && uv run gworkspace docs structure
cd ~/.gworkspace && uv run gworkspace docs append "Text"
cd ~/.gworkspace && uv run gworkspace docs --doc-id "<id>" download "/tmp/export" 1.0
cd ~/.gworkspace && uv run gworkspace docs upload "/tmp/export/doc.md" 1.2
```

### Sheets

```bash
cd ~/.gworkspace && uv run gworkspace sheets read
cd ~/.gworkspace && uv run gworkspace sheets read "BOM!A1:Z100"
cd ~/.gworkspace && uv run gworkspace sheets update "BOM!A2:D2" "A|B|C|D"
cd ~/.gworkspace && uv run gworkspace sheets append "BOM!A:A" "Item|Desc|100"
```

### Gmail

```bash
cd ~/.gworkspace && uv run gworkspace gmail list 10
cd ~/.gworkspace && uv run gworkspace gmail list 20 "from:example.com"
cd ~/.gworkspace && uv run gworkspace gmail get <message_id>
cd ~/.gworkspace && uv run gworkspace gmail body <message_id>
cd ~/.gworkspace && uv run gworkspace gmail draft "to@example.com" "Subject" "Body"
cd ~/.gworkspace && uv run gworkspace gmail send --approve-send "to@example.com" "Subject" "Body"
```

## Authentication Issues

If you see `insufficient authentication scopes` or `invalid_scope`:

```bash
rm -f ~/.gworkspace/token.json
cd ~/.gworkspace && uv run gworkspace gmail list 1
```

## Email Footer

AI-created emails append footer from `~/.gworkspace/email_footer.md`.

Default: `gesendet von KI, iA`

Customize:
```bash
echo "Your custom footer" > ~/.gworkspace/email_footer.md
```

## Project Structure

```
~/.gworkspace/
├── google_workspace_tools/   # Python package
│   ├── auth.py
│   ├── cli.py
│   ├── docs.py
│   ├── sheets.py
│   └── gmail.py
├── client_secrets.json       # OAuth credentials
├── token.json                # Auto-generated token
├── email_footer.md           # Email footer
└── install.sh
```

## API Links

- **Docs:** https://console.developers.google.com/apis/api/docs.googleapis.com/overview?project=667256544145
- **Sheets:** https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=667256544145
- **Gmail:** https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=667256544145

## Notes

- Uses `uv` for dependency management
- One shared `token.json` for all services
- Different services require different OAuth scopes - re-auth if switching
- Sending requires explicit `--approve-send` flag
