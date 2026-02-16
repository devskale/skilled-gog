from __future__ import annotations

import argparse
import sys

from . import __version__
from .docs import run_command as run_docs
from .gmail import run_command as run_gmail
from .sheets import run_command as run_sheets

DEFAULT_DOC_ID = "1kJG9gFMy4M2iHfdxOhQ_KfNh1oy1P4aOdsDB-9626eg"
DEFAULT_SHEET_ID = "1MYNuzKqGEQszGO5iegXMWBzis7zdTSdvg4F3-kFWm-Q"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gworkspace", description="Google Workspace API tools")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="service", required=True)

    docs_parser = subparsers.add_parser("docs", help="Google Docs operations")
    docs_parser.add_argument(
        "command",
        choices=["recent", "structure", "append", "insert", "replace", "paragraph", "bold"],
    )
    docs_parser.add_argument("args", nargs="*")
    docs_parser.add_argument("--doc-id", default=DEFAULT_DOC_ID)

    sheets_parser = subparsers.add_parser("sheets", help="Google Sheets operations")
    sheets_parser.add_argument("command", choices=["read", "update", "append", "clear", "batch"])
    sheets_parser.add_argument("args", nargs="*")
    sheets_parser.add_argument("--sheet-id", default=DEFAULT_SHEET_ID)

    gmail_parser = subparsers.add_parser("gmail", help="Gmail operations")
    gmail_parser.add_argument("command", choices=["list", "get", "body", "draft", "send"])
    gmail_parser.add_argument("args", nargs="*")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args, unknown = parser.parse_known_args(argv)

    if args.service == "docs":
        return run_docs(args.command, args.doc_id, args.args)
    if args.service == "sheets":
        return run_sheets(args.command, args.sheet_id, args.args)
    if args.service == "gmail":
        # Allow gmail subcommands to consume pass-through flags like --approve-send.
        if unknown:
            args.args.extend(unknown)
        return run_gmail(args.command, args.args)

    print("Unknown service")
    return 2


if __name__ == "__main__":
    sys.exit(main())
