from base64 import urlsafe_b64decode

from google_workspace_tools.gmail import build_raw_message


def test_build_raw_message_contains_headers_and_body():
    raw = build_raw_message("alice@example.com", "Hello", "Draft body")
    decoded = urlsafe_b64decode(raw.encode("utf-8")).decode("utf-8")

    assert "To: alice@example.com" in decoded
    assert "Subject: Hello" in decoded
    assert "Draft body" in decoded
    assert "gesendet von KI, iA" in decoded
