from __future__ import annotations

from datetime import datetime, timezone

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .auth import AuthError, get_credentials

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
]


def _service():
    creds = get_credentials(SCOPES)
    return build("docs", "v1", credentials=creds)


def get_document(doc_id: str) -> dict:
    return _service().documents().get(documentId=doc_id).execute()


def list_recent_documents(limit: int = 10) -> list[dict]:
    creds = get_credentials(SCOPES)
    service = build("drive", "v3", credentials=creds)
    result = (
        service.files()
        .list(
            q="mimeType='application/vnd.google-apps.document' and trashed=false",
            orderBy="modifiedTime desc",
            pageSize=limit,
            fields=(
                "files(id,name,modifiedTime,webViewLink,"
                "lastModifyingUser(displayName,emailAddress))"
            ),
        )
        .execute()
    )
    return result.get("files", [])


def print_recent_documents(limit: int = 10) -> None:
    files = list_recent_documents(limit)
    if not files:
        print("No Google Docs found.")
        return

    print(f"Latest edited Google Docs (top {len(files)}):")
    for index, item in enumerate(files, start=1):
        modified = item.get("modifiedTime", "")
        try:
            modified_dt = datetime.fromisoformat(modified.replace("Z", "+00:00"))
            modified_str = modified_dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        except ValueError:
            modified_str = modified
        user = item.get("lastModifyingUser", {}).get("displayName") or "Unknown"
        print(f"{index}. {item.get('name', '(untitled)')}")
        print(f"   modified: {modified_str} by {user}")
        print(f"   id: {item.get('id', '')}")
        print(f"   link: {item.get('webViewLink', '')}")


def print_structure(doc: dict) -> None:
    content = doc.get("body", {}).get("content", [])
    print(f"Document: {doc.get('title')}")
    print(f"Total elements: {len(content)}")
    print()

    for i, element in enumerate(content):
        if "paragraph" in element:
            text = extract_text_from_paragraph(element["paragraph"])
            print(f"{i}: Paragraph - {text[:80]}...")
        elif "table" in element:
            print(f"{i}: Table")
        elif "sectionBreak" in element:
            print(f"{i}: Section Break")


def extract_text_from_paragraph(para: dict) -> str:
    text = ""
    for elem in para.get("elements", []):
        if "textRun" in elem:
            text += elem["textRun"].get("content", "")
    return text


def find_text_index(doc: dict, search_text: str) -> int | None:
    content = doc.get("body", {}).get("content", [])
    current_index = 1

    for element in content:
        if "paragraph" not in element:
            continue
        for elem in element["paragraph"].get("elements", []):
            if "textRun" not in elem:
                continue
            text = elem["textRun"].get("content", "")
            if search_text in text:
                return current_index + text.index(search_text)
            current_index += len(text)

    return None


def _end_index(doc: dict) -> int:
    return doc.get("body", {}).get("content", [{}])[-1].get("endIndex", 1) - 1


def _batch_update(doc_id: str, requests: list[dict]) -> None:
    _service().documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()


def append_text(doc_id: str, text: str) -> None:
    doc = get_document(doc_id)
    requests = [{"insertText": {"location": {"index": _end_index(doc)}, "text": text}}]
    _batch_update(doc_id, requests)


def add_paragraph(doc_id: str, text: str) -> None:
    doc = get_document(doc_id)
    requests = [{"insertText": {"location": {"index": _end_index(doc)}, "text": f"\n{text}"}}]
    _batch_update(doc_id, requests)


def insert_after_text(doc_id: str, after_text: str, new_text: str) -> None:
    doc = get_document(doc_id)
    index = find_text_index(doc, after_text)
    if index is None:
        raise ValueError(f"Text not found: {after_text}")

    requests = [
        {
            "insertText": {
                "location": {"index": index + len(after_text)},
                "text": new_text,
            }
        }
    ]
    _batch_update(doc_id, requests)


def replace_text(doc_id: str, old_text: str, new_text: str) -> None:
    requests = [
        {
            "replaceAllText": {
                "containsText": {"text": old_text},
                "replaceText": new_text,
            }
        }
    ]
    _batch_update(doc_id, requests)


def make_bold(doc_id: str, start_text: str, end_text: str | None = None) -> None:
    doc = get_document(doc_id)
    start_index = find_text_index(doc, start_text)
    if start_index is None:
        raise ValueError(f"Text not found: {start_text}")

    if end_text:
        end_index_start = find_text_index(doc, end_text)
        if end_index_start is None:
            raise ValueError(f"End text not found: {end_text}")
        end_index = end_index_start + len(end_text)
    else:
        end_index = start_index + len(start_text)

    requests = [
        {
            "updateTextStyle": {
                "range": {"startIndex": start_index, "endIndex": end_index},
                "textStyle": {"bold": True},
                "fields": "bold",
            }
        }
    ]
    _batch_update(doc_id, requests)


def run_command(command: str, doc_id: str, args: list[str]) -> int:
    try:
        if command == "recent":
            limit = int(args[0]) if args else 10
            print_recent_documents(limit)
        elif command == "structure":
            print_structure(get_document(doc_id))
        elif command == "append":
            append_text(doc_id, args[0])
            print("OK: appended")
        elif command == "insert":
            insert_after_text(doc_id, args[0], args[1])
            print("OK: inserted")
        elif command == "replace":
            replace_text(doc_id, args[0], args[1])
            print("OK: replaced")
        elif command == "paragraph":
            add_paragraph(doc_id, args[0])
            print("OK: paragraph added")
        elif command == "bold":
            make_bold(doc_id, args[0], args[1] if len(args) > 1 else None)
            print("OK: bold applied")
        else:
            print(f"Unknown docs command: {command}")
            return 2
        return 0
    except (AuthError, ValueError, HttpError) as exc:
        print(f"Error: {exc}")
        return 1
