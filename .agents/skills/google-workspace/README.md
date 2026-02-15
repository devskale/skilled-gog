# Google Workspace API Tools

A pi skill for interacting with Google Docs, Sheets, and Gmail APIs directly - no file conversions needed!

## Quick Start

1. **Create Google Cloud project** and enable APIs (see SKILL.md for details)
2. **Download OAuth credentials** as `client_secrets.json`
3. **Install dependencies:**
   ```bash
   uv sync
   ```
4. **Authenticate** (run any command - it will prompt for auth):
   ```bash
   ./gdocs --help
   ```

## Documentation

See [SKILL.md](SKILL.md) for complete documentation including:
- Detailed setup instructions
- Usage examples for Docs, Sheets, and Gmail
- Troubleshooting guide
- API reference links

## Quick Examples

### Google Docs
```bash
./gdocs structure <doc_id>
./gdocs append <doc_id> "New text at the end"
./gdocs replace <doc_id> "old text" "new text"
./gdocs open <doc_id>
```

### Google Sheets
```bash
./gsheets read <sheet_id>
./gsheets update <sheet_id> "Sheet1!A1" "New Value"
./gsheets append <sheet_id> "Sheet1!A:A" "Item|Description|100"
./gsheets open <sheet_id>
```

### Gmail
```bash
./gmail list
./gmail get <message_id>
./gmail body <message_id>
./gmail open
```

## Files

- `SKILL.md` - Complete documentation and usage guide
- `gdocs` / `gdocs_edit.py` - Google Docs editor
- `gsheets` / `google_sheets_api.py` - Google Sheets editor
- `gmail` / `google_gmail_api.py` - Gmail reader
- `pyproject.toml` - Dependencies
- `client_secrets.json` - OAuth credentials (you create this)
- `token.json` - OAuth token (auto-generated)

## Finding Document/Sheet IDs

- **Google Docs**: `https://docs.google.com/document/d/<DOC_ID>/edit`
- **Google Sheets**: `https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit`

Copy the `<DOC_ID>` or `<SHEET_ID>` from the URL.

## License

This skill is provided as-is for use with the pi coding agent.
