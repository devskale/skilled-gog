from __future__ import annotations

import base64
from email.message import EmailMessage
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .auth import AuthError, get_credentials

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]
DEFAULT_FOOTER = "gesendet von KI, iA"


def get_ai_footer() -> str:
    """Read AI footer from email_footer.md, fall back to default."""
    footer_file = Path(__file__).parent.parent / "email_footer.md"
    if footer_file.exists():
        return footer_file.read_text().strip()
    return DEFAULT_FOOTER


def _service():
    creds = get_credentials(SCOPES)
    return build("gmail", "v1", credentials=creds)


def list_messages(max_results: int = 10, query: str = "", labels: list[str] | None = None) -> list[dict]:
    response = (
        _service()
        .users()
        .messages()
        .list(
            userId="me",
            maxResults=max_results,
            q=query,
            labelIds=labels or None,
        )
        .execute()
    )
    return response.get("messages", [])


def get_message(message_id: str, fmt: str = "full") -> dict:
    return _service().users().messages().get(userId="me", id=message_id, format=fmt).execute()


def build_raw_message(to: str, subject: str, body: str, cc: str | None = None, bcc: str | None = None) -> str:
    """Build a raw email message with AI footer."""
    msg = EmailMessage()
    msg["To"] = to
    msg["Subject"] = subject
    if cc:
        msg["Cc"] = cc
    if bcc:
        msg["Bcc"] = bcc

    ai_footer = get_ai_footer()
    content = body.rstrip()
    if ai_footer and ai_footer not in content:
        content = f"{content}\n\n{ai_footer}" if content else ai_footer
    msg.set_content(content)
    return base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")


def create_draft(to: str, subject: str, body: str, cc: str | None = None, bcc: str | None = None) -> dict:
    """Create an email draft."""
    raw_message = build_raw_message(to, subject, body, cc, bcc)
    return (
        _service()
        .users()
        .drafts()
        .create(userId="me", body={"message": {"raw": raw_message}})
        .execute()
    )


def send_message(to: str, subject: str, body: str, cc: str | None = None, bcc: str | None = None) -> dict:
    """Send an email message."""
    raw_message = build_raw_message(to, subject, body, cc, bcc)
    return _service().users().messages().send(userId="me", body={"raw": raw_message}).execute()


def get_message_body(message: dict) -> str:
    payload = message.get("payload", {})

    def decode(part: dict) -> str | None:
        data = part.get("body", {}).get("data")
        if not data:
            return None
        try:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        except Exception:
            return None

    direct = decode(payload)
    if direct:
        return direct

    for part in payload.get("parts", []):
        part_text = decode(part)
        if part_text:
            return part_text
        for nested in part.get("parts", []):
            nested_text = decode(nested)
            if nested_text:
                return nested_text

    return "[Body could not be extracted]"


def print_header(message: dict) -> None:
    headers = message.get("payload", {}).get("headers", [])
    h = {entry.get("name", ""): entry.get("value", "") for entry in headers}
    print("=" * 80)
    print(f"Subject: {h.get('Subject', '(No subject)')}")
    print(f"From: {h.get('From', '(Unknown sender)')}")
    print(f"Date: {h.get('Date', '(Unknown date)')}")
    print(f"ID: {message.get('id', 'Unknown')}")
    print("=" * 80)


def run_command(command: str, args: list[str]) -> int:
    try:
        if command == "list":
            max_results = int(args[0]) if args else 10
            query = args[1] if len(args) > 1 else ""
            labels = args[2].split(",") if len(args) > 2 and args[2] else None
            messages = list_messages(max_results, query, labels)
            print(f"Found {len(messages)} messages")
            for msg in messages:
                full_msg = get_message(msg["id"], fmt="full")
                print_header(full_msg)
                body = get_message_body(full_msg)
                print(body[:500] + ("..." if len(body) > 500 else ""))
                print()
            return 0

        if command == "get":
            message = get_message(args[0], fmt="full")
            print_header(message)
            print(get_message_body(message))
            return 0

        if command == "body":
            message = get_message(args[0], fmt="full")
            print(get_message_body(message))
            return 0

        if command == "draft":
            if len(args) < 3:
                print("Usage: gworkspace gmail draft <to> <subject> <body...>")
                return 2
            to = args[0]
            subject = args[1]
            body = " ".join(args[2:]) if len(args) > 2 else ""
            cc = args[3] if len(args) > 3 else None
            draft = create_draft(to, subject, body, cc)
            print(f"Draft created: {draft.get('id', '')}")
            print("Open drafts: https://mail.google.com/mail/u/0/#drafts")
            return 0

        if command == "send":
            if "--approve-send" not in args:
                print(
                    "Refused: send requires explicit approval flag.\n"
                    "Usage: gworkspace gmail send --approve-send <to> <subject> <body...>"
                )
                return 2

            filtered_args = [arg for arg in args if arg != "--approve-send"]
            if len(filtered_args) < 3:
                print("Usage: gworkspace gmail send --approve-send <to> <subject> <body...>")
                return 2

            to = filtered_args[0]
            subject = filtered_args[1]
            body = " ".join(filtered_args[2:]) if len(filtered_args) > 2 else ""
            cc = filtered_args[3] if len(filtered_args) > 3 else None
            sent = send_message(to, subject, body, cc)
            print(f"Message sent: {sent.get('id', '')}")
            print(f"  To: {to}")
            print(f"  Subject: {subject}")
            return 0

        print(f"Unknown gmail command: {command}")
        return 2
    except (AuthError, ValueError, IndexError, HttpError) as exc:
        print(f"Error: {exc}")
        return 1
