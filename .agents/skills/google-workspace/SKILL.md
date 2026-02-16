---
name: google-workspace
description: Operate Google Docs, Google Sheets, and Gmail from this workspace using OAuth and uv. Use for reading/editing docs and sheets, and reading/drafting/sending mail.
---

# Google Workspace Skill

Use this skill with the project at:

`/Users/johannwaldherr/code/google`

This skill is paired with the local Python project and wrappers:
- `uv run gworkspace ...`
- `./gdocs ...`
- `./gsheets ...`
- `./gmail ...`

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
cd /Users/johannwaldherr/code/google
rm -f token.json
# then run the service command again, e.g.
./gmail list 1
```

## Commands

### Unified CLI (preferred)

```bash
# Docs
uv run gworkspace docs recent 10
uv run gworkspace docs structure
uv run gworkspace docs append "Text"
uv run gworkspace docs insert "anchor" "new text"
uv run gworkspace docs replace "old" "new"
uv run gworkspace docs paragraph "Heading"
uv run gworkspace docs bold "Important"

# Sheets
uv run gworkspace sheets read
uv run gworkspace sheets read "BOM!A1:Z100"
uv run gworkspace sheets update "BOM!A2:D2" "A|B|C|D"
uv run gworkspace sheets append "BOM!A:A" "Item|Description|100"
uv run gworkspace sheets clear "BOM!A2:Z1000"
uv run gworkspace sheets batch update.json

# Gmail
uv run gworkspace gmail list 10
uv run gworkspace gmail list 20 "from:wibke"
uv run gworkspace gmail get <message_id>
uv run gworkspace gmail body <message_id>
uv run gworkspace gmail draft "alice@example.com" "Subject" "Body text"
uv run gworkspace gmail send --approve-send "alice@example.com" "Subject" "Body text"
```

### Wrappers (same behavior)

```bash
./gdocs recent 10
./gdocs structure
./gsheets read
./gmail list
./gmail list 20 "from:wibke"
./gmail draft "alice@example.com" "Subject" "Body text"
./gmail send --approve-send "alice@example.com" "Subject" "Body text"
```

Use custom sheet id with wrapper:

```bash
./gsheets --id <sheet_id> read "Sheet1!A1:C20"
```

## Defaults

- Default document id: `1kJG9gFMy4M2iHfdxOhQ_KfNh1oy1P4aOdsDB-9626eg`
- Default sheet id: `1MYNuzKqGEQszGO5iegXMWBzis7zdTSdvg4F3-kFWm-Q`

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
- AI-created emails (draft/send) always append footer: `gesendet von KI, iA`.
- Sending policy: use `send` only after explicit user approval; command requires `--approve-send`.
