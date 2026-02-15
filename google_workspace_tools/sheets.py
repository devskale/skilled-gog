from __future__ import annotations

import csv
import json
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .auth import AuthError, get_credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def _service():
    creds = get_credentials(SCOPES)
    return build("sheets", "v4", credentials=creds)


def parse_values_arg(values: list[str]) -> list[list[str]]:
    if not values:
        raise ValueError("No values provided")
    if len(values) > 1:
        return [values]
    single = values[0]
    if "|" in single:
        return [[v.strip() for v in single.split("|")]]
    if "," in single:
        return [[v.strip() for v in single.split(",")]]
    return [[single]]


def print_values(values: list[list[str]], max_rows: int = 100) -> None:
    if not values:
        print("No data found.")
        return

    num_cols = max(len(row) for row in values)
    col_widths = [0] * num_cols

    for row in values[:20]:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    col_widths = [min(w, 50) for w in col_widths]

    sep = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    print(sep)
    for i, row in enumerate(values[:max_rows]):
        padded = row + [""] * (num_cols - len(row))
        cells = [str(cell)[:col_widths[j]].ljust(col_widths[j]) for j, cell in enumerate(padded)]
        print("| " + " | ".join(cells) + " |")
        if i == 0:
            print(sep)
    print(sep)


def save_csv(values: list[list[str]], output_file: str, sheet_title: str | None = None) -> None:
    path = Path(output_file)
    mode = "a" if sheet_title and path.exists() else "w"
    with path.open(mode, newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if sheet_title and mode == "a":
            file.write(f"\n\n# Sheet: {sheet_title}\n")
        writer.writerows(values)


def read_sheet(sheet_id: str, range_name: str | None = None, output_file: str | None = None) -> None:
    service = _service()
    metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    sheets = metadata.get("sheets", [])

    print(f"Spreadsheet: {metadata.get('properties', {}).get('title', 'Unknown')}")
    print(f"URL: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
    print()

    if range_name:
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_name).execute()
        values = result.get("values", [])
        print(f"=== Range: {range_name} ===")
        print_values(values)
        if output_file:
            save_csv(values, output_file)
        return

    for sheet in sheets:
        title = sheet.get("properties", {}).get("title", "Unknown")
        print(f"=== Sheet: {title} ===")
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=title).execute()
        values = result.get("values", [])
        print_values(values)
        if output_file:
            save_csv(values, output_file, sheet_title=title)


def update_values(sheet_id: str, range_name: str, values: list[list[str]]) -> None:
    _service().spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        body={"values": values},
    ).execute()


def append_values(sheet_id: str, range_name: str, values: list[list[str]]) -> None:
    _service().spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        body={"values": values},
        insertDataOption="INSERT_ROWS",
    ).execute()


def clear_values(sheet_id: str, range_name: str) -> None:
    _service().spreadsheets().values().clear(spreadsheetId=sheet_id, range=range_name).execute()


def batch_update(sheet_id: str, json_file: str) -> None:
    with open(json_file, encoding="utf-8") as file:
        payload = json.load(file)
    data = payload.get("data", payload)
    _service().spreadsheets().values().batchUpdate(
        spreadsheetId=sheet_id,
        body={"valueInputOption": "USER_ENTERED", "data": data},
    ).execute()


def run_command(command: str, sheet_id: str, args: list[str]) -> int:
    try:
        if command == "read":
            range_name = args[0] if args else None
            output_file = args[1] if len(args) > 1 else None
            read_sheet(sheet_id, range_name, output_file)
            return 0

        if command == "update":
            update_values(sheet_id, args[0], parse_values_arg(args[1:]))
            print("OK: updated")
            return 0

        if command == "append":
            append_values(sheet_id, args[0], parse_values_arg(args[1:]))
            print("OK: appended")
            return 0

        if command == "clear":
            clear_values(sheet_id, args[0])
            print("OK: cleared")
            return 0

        if command == "batch":
            batch_update(sheet_id, args[0])
            print("OK: batch updated")
            return 0

        print(f"Unknown sheets command: {command}")
        return 2
    except (AuthError, ValueError, IndexError, HttpError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}")
        return 1
