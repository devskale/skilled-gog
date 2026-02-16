from __future__ import annotations

import base64
from datetime import datetime, timezone
import mimetypes
from pathlib import Path
import re
from urllib.request import Request, urlopen

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaInMemoryUpload

from .auth import AuthError, get_credentials

DOC_SCOPES = [
    "https://www.googleapis.com/auth/documents",
]
DRIVE_READ_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
DRIVE_WRITE_SCOPES = ["https://www.googleapis.com/auth/drive"]


def _service():
    creds = get_credentials(DOC_SCOPES)
    return build("docs", "v1", credentials=creds)


def _drive_service(scopes: list[str]):
    creds = get_credentials(scopes)
    return build("drive", "v3", credentials=creds)


def get_document(doc_id: str, include_tabs_content: bool = False) -> dict:
    if include_tabs_content:
        return _service().documents().get(documentId=doc_id, includeTabsContent=True).execute()
    return _service().documents().get(documentId=doc_id).execute()


def list_recent_documents(limit: int = 10) -> list[dict]:
    service = _drive_service(DRIVE_READ_SCOPES)
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


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return cleaned.strip("_") or "document"


def _split_frontmatter(markdown_text: str) -> tuple[dict[str, str], str]:
    if not markdown_text.startswith("---\n"):
        return {}, markdown_text

    end = markdown_text.find("\n---\n", 4)
    if end == -1:
        return {}, markdown_text

    front = markdown_text[4:end]
    body = markdown_text[end + 5 :]
    meta: dict[str, str] = {}
    for line in front.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, body


def _truncate_meta(value: str, max_len: int = 120) -> str:
    value = value.strip()
    return value[:max_len] if len(value) > max_len else value


def _build_app_properties(metadata: dict[str, str], version: str, markdown_path: Path) -> dict[str, str]:
    props: dict[str, str] = {"import_version": _truncate_meta(version)}
    mapping = {
        "doc_id": "source_doc_id",
        "doc_url": "source_doc_url",
        "title": "source_title",
        "exported_at": "source_exported_at",
        "drive_parent_id": "source_parent_id",
    }
    for src_key, dst_key in mapping.items():
        if metadata.get(src_key):
            props[dst_key] = _truncate_meta(metadata[src_key])
    props["source_markdown"] = _truncate_meta(markdown_path.name)
    return props


def _build_visible_header(metadata: dict[str, str], version: str, markdown_path: Path) -> str:
    src_title = metadata.get("title", markdown_path.stem)
    src_id = metadata.get("doc_id", "unknown")
    src_url = metadata.get("doc_url", "")
    url_fragment = f" | URL: {src_url}" if src_url else ""
    return f"_Imported from Markdown ({src_title}) | Source ID: {src_id} | Version: V{version}{url_fragment}_\n\n"


def _extract_data_images(markdown_text: str, img_dir: Path) -> tuple[str, int]:
    img_dir.mkdir(parents=True, exist_ok=True)
    definitions = re.findall(
        r"^\[([^\]]+)\]:\s*<data:(image/[^;>]+);base64,([^>]+)>$",
        markdown_text,
        flags=re.MULTILINE,
    )
    if not definitions:
        return markdown_text, 0

    key_to_file: dict[str, str] = {}
    for key, mime_type, b64_payload in definitions:
        ext = mimetypes.guess_extension(mime_type) or ".bin"
        filename = f"{_slugify(key)}{ext}"
        target = img_dir / filename
        target.write_bytes(base64.b64decode(b64_payload))
        key_to_file[key] = filename

    for key, filename in key_to_file.items():
        markdown_text = re.sub(
            rf"!\[([^\]]*)\]\[{re.escape(key)}\]",
            rf"![\1](img/{filename})",
            markdown_text,
        )
        markdown_text = re.sub(
            rf"^\[{re.escape(key)}\]:\s*<data:image/[^;>]+;base64,[^>]+>\s*$\n?",
            "",
            markdown_text,
            flags=re.MULTILINE,
        )

    return markdown_text, len(key_to_file)


def _embed_local_images(markdown_text: str, markdown_path: Path) -> str:
    pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

    def replacer(match: re.Match[str]) -> str:
        alt = match.group(1)
        img_ref = match.group(2).strip()
        if img_ref.startswith("http://") or img_ref.startswith("https://") or img_ref.startswith("data:"):
            return match.group(0)
        image_path = (markdown_path.parent / img_ref).resolve()
        if not image_path.exists() or not image_path.is_file():
            return match.group(0)
        mime_type, _ = mimetypes.guess_type(str(image_path))
        mime_type = mime_type or "application/octet-stream"
        encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
        return f"![{alt}](data:{mime_type};base64,{encoded})"

    return pattern.sub(replacer, markdown_text)


def _heading_from_named_style(named_style: str | None) -> int | None:
    if not named_style:
        return None
    match = re.match(r"HEADING_(\d+)$", named_style)
    if not match:
        return None
    return max(1, min(6, int(match.group(1))))


def _apply_text_style(text: str, style: dict) -> str:
    if not text:
        return text
    url = style.get("link", {}).get("url") if style else None
    bold = bool(style.get("bold")) if style else False
    italic = bool(style.get("italic")) if style else False

    rendered = text
    if bold and italic:
        rendered = f"***{rendered}***"
    elif bold:
        rendered = f"**{rendered}**"
    elif italic:
        rendered = f"*{rendered}*"

    if url:
        rendered = f"[{rendered}]({url})"
    return rendered


def _download_image(uri: str, img_dir: Path, filename: str) -> Path:
    img_dir.mkdir(parents=True, exist_ok=True)
    target = img_dir / filename
    if target.exists():
        return target

    request = Request(uri, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=30) as response:
        data = response.read()
        content_type = response.headers.get("Content-Type", "")
    suffix = mimetypes.guess_extension(content_type.split(";")[0].strip()) if content_type else None
    if suffix and target.suffix != suffix:
        target = target.with_suffix(suffix)
    target.write_bytes(data)
    return target


def _paragraph_to_markdown(
    paragraph: dict,
    inline_objects: dict,
    image_cache: dict[str, str],
    img_dir: Path,
    image_counter: list[int],
) -> str:
    chunks: list[str] = []
    for element in paragraph.get("elements", []):
        if "textRun" in element:
            run = element["textRun"]
            content = run.get("content", "")
            content = content.replace("\r", "")
            content = content.replace("\n", "")
            if content:
                chunks.append(_apply_text_style(content, run.get("textStyle", {})))
        elif "inlineObjectElement" in element:
            object_id = element["inlineObjectElement"].get("inlineObjectId", "")
            if not object_id:
                continue
            if object_id not in image_cache:
                obj = inline_objects.get(object_id, {})
                uri = (
                    obj.get("inlineObjectProperties", {})
                    .get("embeddedObject", {})
                    .get("imageProperties", {})
                    .get("contentUri", "")
                )
                if uri:
                    image_counter[0] += 1
                    filename = f"image{image_counter[0]}.png"
                    local = _download_image(uri, img_dir, filename)
                    image_cache[object_id] = local.name
            if object_id in image_cache:
                chunks.append(f"![]({'img/' + image_cache[object_id]})")

    text = "".join(chunks).strip()
    if not text:
        return ""

    named_style = paragraph.get("paragraphStyle", {}).get("namedStyleType")
    heading_level = _heading_from_named_style(named_style)
    if heading_level:
        return f"{'#' * heading_level} {text}"
    if paragraph.get("bullet"):
        return f"- {text}"
    return text


def _tab_to_markdown_lines(
    tab: dict,
    depth: int,
    lines: list[str],
    image_cache: dict[str, str],
    img_dir: Path,
    image_counter: list[int],
) -> None:
    props = tab.get("tabProperties", {})
    title = props.get("title", "Untitled Tab")
    # Always flatten tabs to top-level H1 headings in markdown export.
    lines.append(f"# {title}")
    lines.append("")

    document_tab = tab.get("documentTab", {})
    inline_objects = document_tab.get("inlineObjects", {})
    for element in document_tab.get("body", {}).get("content", []):
        if "paragraph" in element:
            line = _paragraph_to_markdown(
                element["paragraph"], inline_objects, image_cache, img_dir, image_counter
            )
            if line:
                lines.append(line)
        elif "table" in element:
            lines.append("[Table omitted in markdown export]")
        elif "tableOfContents" in element:
            lines.append("[Table of contents omitted in markdown export]")
    lines.append("")

    child_tabs = sorted(
        tab.get("childTabs", []),
        key=lambda t: t.get("tabProperties", {}).get("index", 0),
    )
    for child in child_tabs:
        _tab_to_markdown_lines(child, depth + 1, lines, image_cache, img_dir, image_counter)


def _render_tabs_markdown(doc: dict, img_dir: Path) -> tuple[str, int]:
    tabs = sorted(doc.get("tabs", []), key=lambda t: t.get("tabProperties", {}).get("index", 0))
    lines: list[str] = []
    image_cache: dict[str, str] = {}
    image_counter = [0]
    for tab in tabs:
        _tab_to_markdown_lines(tab, 0, lines, image_cache, img_dir, image_counter)
    return "\n".join(lines).strip() + "\n", image_counter[0]


def export_markdown(doc_id: str, out_dir_arg: str | None = None, version: str = "1.0") -> Path:
    drive = _drive_service(DRIVE_READ_SCOPES)
    file_meta = (
        drive.files()
        .get(fileId=doc_id, fields="id,name,webViewLink,parents")
        .execute()
    )
    doc_name = file_meta.get("name", "document")

    if out_dir_arg:
        root_dir = Path(out_dir_arg)
        markdown_filename = "doc.md"
    else:
        slug = _slugify(doc_name)
        root_dir = Path("docs") / slug
        markdown_filename = f"{slug}.md"

    root_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = root_dir / markdown_filename
    img_dir = root_dir / "img"

    doc_with_tabs = get_document(doc_id, include_tabs_content=True)
    if doc_with_tabs.get("tabs"):
        rewritten_markdown, image_count = _render_tabs_markdown(doc_with_tabs, img_dir)
    else:
        raw_markdown = (
            drive.files().export(fileId=doc_id, mimeType="text/markdown").execute().decode("utf-8", "replace")
        )
        rewritten_markdown, image_count = _extract_data_images(raw_markdown, img_dir)

    frontmatter = "\n".join(
        [
            "---",
            f"doc_id: {file_meta.get('id', doc_id)}",
            f"doc_url: {file_meta.get('webViewLink', f'https://docs.google.com/document/d/{doc_id}/edit')}",
            f"drive_parent_id: {(file_meta.get('parents') or [''])[0]}",
            f"local_dir: {root_dir.as_posix()}",
            f"local_file: {markdown_path.as_posix()}",
            f"title: {doc_name}",
            f"version: {version}",
            f"exported_at: {datetime.now(timezone.utc).isoformat()}",
            "---",
            "",
        ]
    )
    markdown_path.write_text(frontmatter + rewritten_markdown, encoding="utf-8")

    if image_count == 0 and img_dir.exists():
        # Keep structure predictable but avoid stale files.
        for child in img_dir.iterdir():
            if child.is_file():
                child.unlink()

    print(f"OK: exported markdown to {markdown_path}")
    print(f"OK: images extracted: {image_count} -> {img_dir}")
    return markdown_path


def import_markdown(markdown_file: str, version: str) -> dict:
    path = Path(markdown_file).expanduser().resolve()
    if not path.exists():
        raise ValueError(f"Markdown file not found: {path}")

    full_text = path.read_text(encoding="utf-8")
    metadata, body = _split_frontmatter(full_text)
    body = _build_visible_header(metadata, version, path) + _embed_local_images(body, path)

    source_title = metadata.get("title") or path.stem
    source_title = re.sub(r"_V\d+(\.\d+)?$", "", source_title)
    target_name = f"{source_title}_V{version}"
    app_properties = _build_app_properties(metadata, version, path)

    drive = _drive_service(DRIVE_WRITE_SCOPES)
    file_body: dict[str, object] = {
        "name": target_name,
        "mimeType": "application/vnd.google-apps.document",
        "appProperties": app_properties,
    }
    parent_id = metadata.get("drive_parent_id")
    if parent_id:
        file_body["parents"] = [parent_id]

    upload = MediaInMemoryUpload(body.encode("utf-8"), mimetype="text/markdown", resumable=False)
    created = (
        drive.files()
        .create(
            body=file_body,
            media_body=upload,
            fields="id,name,webViewLink,mimeType,appProperties",
        )
        .execute()
    )
    print(f"OK: uploaded markdown as Google Doc {created.get('name', '')}")
    print(f"   id: {created.get('id', '')}")
    print(f"   link: {created.get('webViewLink', '')}")
    print("INFO: markdown upload creates a single-body Google Doc (tab structure is not restored).")
    return created


def run_command(command: str, doc_id: str, args: list[str]) -> int:
    try:
        if command == "recent":
            limit = int(args[0]) if args else 10
            print_recent_documents(limit)
        elif command in ("export-md", "download"):
            out_dir = args[0] if args else None
            version = args[1] if len(args) > 1 else "1.0"
            export_markdown(doc_id, out_dir, version)
            print("OK: markdown export completed")
        elif command in ("import-md", "upload"):
            if len(args) < 2:
                print("Error: upload/import-md requires <markdown_file> <version>")
                return 2
            import_markdown(args[0], args[1])
            print("OK: markdown import completed")
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
