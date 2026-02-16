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


def get_document(doc_id: str, include_tabs_content: bool = False) -> dict:
    if include_tabs_content:
        return _service().documents().get(documentId=doc_id, includeTabsContent=True).execute()
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


def list_tabs(doc_id: str) -> list[dict]:
    """List all tabs in the document including nested child tabs."""
    doc = get_document(doc_id, include_tabs_content=True)
    tabs = doc.get("tabs", [])

    if not tabs:
        print("No tabs found (document may not have tabs enabled)")
        return []

    all_tabs = []

    def collect_tabs(tab_list: list[dict], indent: int = 0) -> None:
        for tab in tab_list:
            props = tab.get("tabProperties", {})
            all_tabs.append({
                "tabId": props.get("tabId", "N/A"),
                "title": props.get("title", "Untitled"),
                "type": "documentTab" if "documentTab" in tab else "other",
                "indent": indent
            })
            # Recursively collect child tabs
            if "childTabs" in tab:
                collect_tabs(tab["childTabs"], indent + 1)

    collect_tabs(tabs)
    return all_tabs


def print_tabs(doc_id: str) -> None:
    """Print all tabs in a formatted table."""
    tabs = list_tabs(doc_id)

    if not tabs:
        return

    print(f"\nTabs ({len(tabs)} total):")
    print("-" * 80)
    print(f"{'Tab ID':<20} {'Title':<40} {'Type':<15}")
    print("-" * 80)

    for tab in tabs:
        indent = "  " * tab["indent"]
        print(f"{indent}{tab['tabId']:<20} {tab['title']:<40} {tab['type']:<15}")


def create_tab(doc_id: str, title: str, parent_tab_id: str | None = None, index: int | None = None) -> None:
    """Create a new tab in the document."""
    from typing import Any
    tab_props: dict[str, Any] = {"title": title}
    if parent_tab_id:
        tab_props["parentTabId"] = parent_tab_id
    if index is not None:
        tab_props["index"] = index

    requests = [{"createTab": {"tabProperties": tab_props}}]
    _batch_update(doc_id, requests)


def delete_tab(doc_id: str, tab_id: str) -> None:
    """Delete a tab from the document."""
    requests = [{"deleteTab": {"tabId": tab_id}}]
    _batch_update(doc_id, requests)


def rename_tab(doc_id: str, tab_id: str, new_title: str) -> None:
    """Rename a tab."""
    requests = [
        {
            "updateTabProperties": {
                "tabProperties": {"tabId": tab_id, "title": new_title},
                "fields": "title"
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
        elif command == "tabs":
            if not args:
                print("Error: tabs command requires a subcommand (list, create, delete, rename)")
                return 2
            subcommand = args[0]
            if subcommand == "list":
                print_tabs(doc_id)
                print("OK: tabs listed")
            elif subcommand == "create":
                if len(args) < 2:
                    print("Error: tabs create requires a title")
                    return 2
                title = args[1]
                parent_id = args[2] if len(args) > 2 else None
                create_tab(doc_id, title, parent_id)
                print(f"OK: tab '{title}' created")
            elif subcommand == "delete":
                if len(args) < 2:
                    print("Error: tabs delete requires a tab_id")
                    return 2
                delete_tab(doc_id, args[1])
                print(f"OK: tab {args[1]} deleted")
            elif subcommand == "rename":
                if len(args) < 3:
                    print("Error: tabs rename requires tab_id and new title")
                    return 2
                rename_tab(doc_id, args[1], args[2])
                print(f"OK: tab renamed to '{args[2]}'")
            else:
                print(f"Unknown tabs subcommand: {subcommand}")
                return 2
        else:
            print(f"Unknown docs command: {command}")
            return 2
        return 0
    except (AuthError, ValueError, HttpError) as exc:
        print(f"Error: {exc}")
        return 1
