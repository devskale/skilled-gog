# Google Workspace Tools

A proper Python project for Google Workspace automation with a unified CLI and lightweight wrappers.

## Features

- Google Docs operations: `structure`, `append`, `insert`, `replace`, `paragraph`, `bold`
- Google Sheets operations: `read`, `update`, `append`, `clear`, `batch`
- Gmail operations: `list`, `get`, `body`
- Shared OAuth2 credential flow across all services

## Project Layout

- `google_workspace_tools/` package source
- `tests/` unit tests
- `gdocs`, `gsheets`, `gmail` wrapper commands
- `pyproject.toml` project metadata and CLI entrypoint

## Install

```bash
uv sync
```

## Unified CLI

```bash
# Docs
uv run gworkspace docs structure
uv run gworkspace docs append "Hello"

# Sheets
uv run gworkspace sheets read
uv run gworkspace sheets update "BOM!A2:D2" "Val1|Val2|Val3|Val4"

# Gmail
uv run gworkspace gmail list 10
```

## Wrapper Commands

Wrappers keep the original workflow and default IDs:

```bash
./gdocs structure
./gsheets read
./gmail list 20
```

Custom sheet ID:

```bash
./gsheets --id <sheet_id> read "Sheet1!A1:C10"
```

## Auth Files

- `client_secrets.json` (OAuth client credentials)
- `token.json` (generated access token)

Both are ignored by `.gitignore`.

## Run Tests

```bash
uv run pytest
```
