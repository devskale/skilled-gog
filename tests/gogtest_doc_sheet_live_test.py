from __future__ import annotations

from datetime import datetime, timezone
import uuid

from googleapiclient.discovery import build

from google_workspace_tools.auth import get_credentials

GOGTEST_NAME = "GOGtest"
EDITABLE_NAME = "editable"
DOC_MIME = "application/vnd.google-apps.document"
SHEET_MIME = "application/vnd.google-apps.spreadsheet"


def make_services():
    scopes = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/spreadsheets",
    ]
    creds = get_credentials(scopes)
    return (
        build("drive", "v3", credentials=creds),
        build("docs", "v1", credentials=creds),
        build("sheets", "v4", credentials=creds),
    )


def find_folder_id(drive, name: str, parent_id: str | None = None) -> str | None:
    parts = [
        "mimeType='application/vnd.google-apps.folder'",
        f"name='{name}'",
        "trashed=false",
    ]
    if parent_id:
        parts.append(f"'{parent_id}' in parents")
    q = " and ".join(parts)
    res = drive.files().list(q=q, fields="files(id,name)", pageSize=10).execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None


def ensure_subfolder(drive, parent_id: str, name: str) -> str:
    existing = find_folder_id(drive, name, parent_id)
    if existing:
        return existing
    created = (
        drive.files()
        .create(
            body={
                "name": name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_id],
            },
            fields="id",
        )
        .execute()
    )
    return created["id"]


def list_files(drive, folder_id: str, mime: str) -> list[dict]:
    q = f"'{folder_id}' in parents and mimeType='{mime}' and trashed=false"
    res = drive.files().list(
        q=q,
        fields="files(id,name,webViewLink,mimeType)",
        orderBy="name",
        pageSize=200,
    ).execute()
    return res.get("files", [])


def overwrite_copy(drive, src: dict, editable_id: str) -> dict:
    q = (
        f"'{editable_id}' in parents and mimeType='{src['mimeType']}' "
        f"and name='{src['name']}' and trashed=false"
    )
    existing = drive.files().list(q=q, fields="files(id,name)", pageSize=5).execute().get("files", [])
    for item in existing:
        drive.files().update(fileId=item["id"], body={"trashed": True}).execute()

    copied = (
        drive.files()
        .copy(
            fileId=src["id"],
            body={"name": src["name"], "parents": [editable_id]},
            fields="id,name,webViewLink,mimeType",
        )
        .execute()
    )
    return copied


def doc_contains_marker(docs, doc_id: str, marker: str) -> bool:
    doc = docs.documents().get(documentId=doc_id).execute()
    for element in doc.get("body", {}).get("content", []):
        para = element.get("paragraph")
        if not para:
            continue
        for pe in para.get("elements", []):
            text_run = pe.get("textRun")
            if text_run and marker in text_run.get("content", ""):
                return True
    return False


def main() -> int:
    drive, docs, sheets = make_services()

    print("STEP 1: find dir")
    gogtest_id = find_folder_id(drive, GOGTEST_NAME)
    if not gogtest_id:
        print("FAIL: GOGtest not found")
        return 1
    print(f"PASS: {gogtest_id}")

    print("\nSTEP 2: list docs + sheets")
    docs_in_folder = list_files(drive, gogtest_id, DOC_MIME)
    sheets_in_folder = list_files(drive, gogtest_id, SHEET_MIME)
    if not docs_in_folder:
        print("FAIL: no docs in GOGtest")
        return 2
    if not sheets_in_folder:
        print("FAIL: no sheets in GOGtest")
        return 3

    for d in docs_in_folder:
        print(f"doc: {d['name']} ({d['id']})")
    for s in sheets_in_folder:
        print(f"sheet: {s['name']} ({s['id']})")

    source_doc = docs_in_folder[0]
    source_sheet = sheets_in_folder[0]

    print("\nSTEP 3: backup/overwrite in GOGtest/editable")
    editable_id = ensure_subfolder(drive, gogtest_id, EDITABLE_NAME)
    editable_doc = overwrite_copy(drive, source_doc, editable_id)
    editable_sheet = overwrite_copy(drive, source_sheet, editable_id)
    print(f"PASS: editable doc={editable_doc['id']} sheet={editable_sheet['id']}")

    tag = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    print("\nSTEP 4A: make edit to 1 doc")
    doc_marker = f"[DOC_EDIT_{tag}_{uuid.uuid4().hex[:6]}]"
    docs.documents().batchUpdate(
        documentId=editable_doc["id"],
        body={
            "requests": [
                {
                    "insertText": {
                        "location": {"index": 1},
                        "text": doc_marker + "\n",
                    }
                }
            ]
        },
    ).execute()
    print(f"PASS: doc marker inserted {doc_marker}")

    print("\nSTEP 4B: make edits to 1 sheet")
    sheet_marker = f"SHEET_EDIT_{tag}_{uuid.uuid4().hex[:6]}"
    test_range = "A1"
    sheets.spreadsheets().values().update(
        spreadsheetId=editable_sheet["id"],
        range=test_range,
        valueInputOption="USER_ENTERED",
        body={"values": [[sheet_marker]]},
    ).execute()
    print(f"PASS: sheet updated {test_range}={sheet_marker}")

    print("\nSTEP 5: confirm edits")
    doc_ok = doc_contains_marker(docs, editable_doc["id"], doc_marker)
    sheet_read = (
        sheets.spreadsheets()
        .values()
        .get(spreadsheetId=editable_sheet["id"], range=test_range)
        .execute()
        .get("values", [[]])
    )
    sheet_val = sheet_read[0][0] if sheet_read and sheet_read[0] else ""
    sheet_ok = sheet_val == sheet_marker

    print(f"doc confirm: {'PASS' if doc_ok else 'FAIL'}")
    print(f"sheet confirm: {'PASS' if sheet_ok else 'FAIL'}")

    if not (doc_ok and sheet_ok):
        print("SUMMARY: FAIL")
        return 4

    print("SUMMARY: PASS")
    print(f"editable doc link: {editable_doc.get('webViewLink','')}")
    print(f"editable sheet link: {editable_sheet.get('webViewLink','')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
