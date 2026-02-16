import base64
from pathlib import Path

import pytest

from google_workspace_tools.docs import (
    _build_app_properties,
    _build_visible_header,
    _encode_image_for_data_uri,
    _embed_local_images,
    _extract_data_images,
    _render_tabs_markdown,
    _split_frontmatter,
)


def test_split_frontmatter():
    text = "---\ndoc_id: 123\nversion: 1.0\n---\n\n# Title\n"
    meta, body = _split_frontmatter(text)
    assert meta["doc_id"] == "123"
    assert meta["version"] == "1.0"
    assert body.strip() == "# Title"


def test_extract_data_images_rewrites_to_img_folder(tmp_path: Path):
    md = (
        "# T\n\n"
        "![][image1]\n\n"
        "[image1]: <data:image/png;base64,aGVsbG8=>\n"
    )
    out, count = _extract_data_images(md, tmp_path / "img")
    assert count == 1
    assert "![](img/image1.png)" in out
    assert "[image1]: <data:image" not in out
    assert (tmp_path / "img" / "image1.png").read_bytes() == b"hello"


def test_embed_local_images_to_data_uri(tmp_path: Path):
    md_file = tmp_path / "doc.md"
    img_dir = tmp_path / "img"
    img_dir.mkdir()
    (img_dir / "a.png").write_bytes(b"hello")
    text = "Look ![x](img/a.png)"
    converted = _embed_local_images(text, md_file)
    assert "data:image/png;base64," in converted


def test_encode_image_for_data_uri_downscales_wide_image(tmp_path: Path):
    pil = pytest.importorskip("PIL.Image")
    image_path = tmp_path / "wide.png"
    img = pil.new("RGB", (2000, 1000), "white")
    img.save(image_path, format="PNG")

    mime_type, b64 = _encode_image_for_data_uri(image_path, 580)
    assert mime_type == "image/png"

    data = base64.b64decode(b64)
    resized_path = tmp_path / "resized.png"
    resized_path.write_bytes(data)
    with pil.open(resized_path) as resized:
        assert resized.width == 580


def test_build_app_properties_from_frontmatter(tmp_path: Path):
    meta = {
        "doc_id": "abc123",
        "doc_url": "https://docs.google.com/document/d/abc123/edit",
        "title": "Spec",
        "exported_at": "2026-02-16T00:00:00Z",
        "drive_parent_id": "parent1",
    }
    props = _build_app_properties(meta, "1.2", tmp_path / "doc.md")
    assert props["import_version"] == "1.2"
    assert props["source_doc_id"] == "abc123"
    assert props["source_doc_url"].startswith("https://docs.google.com/document/")
    assert props["source_markdown"] == "doc.md"


def test_build_visible_header_contains_source_data(tmp_path: Path):
    meta = {"title": "Spec", "doc_id": "abc123", "doc_url": "https://example.com"}
    header = _build_visible_header(meta, "1.2", tmp_path / "doc.md")
    assert "Imported from Markdown (Spec)" in header
    assert "Source ID: abc123" in header
    assert "Version: V1.2" in header


def test_render_tabs_markdown_merges_parent_and_child(tmp_path: Path):
    doc = {
        "tabs": [
            {
                "tabProperties": {"title": "Root", "index": 0},
                "documentTab": {
                    "body": {
                        "content": [
                            {
                                "paragraph": {
                                    "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                                    "elements": [{"textRun": {"content": "Root text\n", "textStyle": {}}}],
                                }
                            }
                        ]
                    },
                    "inlineObjects": {},
                },
                "childTabs": [
                    {
                        "tabProperties": {"title": "Child", "index": 0},
                        "documentTab": {
                            "body": {
                                "content": [
                                    {
                                        "paragraph": {
                                            "paragraphStyle": {"namedStyleType": "HEADING_2"},
                                            "elements": [{"textRun": {"content": "Child heading\n", "textStyle": {}}}],
                                        }
                                    }
                                ]
                            },
                            "inlineObjects": {},
                        },
                        "childTabs": [],
                    }
                ],
            }
        ]
    }
    md, image_count = _render_tabs_markdown(doc, tmp_path / "img")
    assert "# Root" in md
    assert "Root text" in md
    assert "# Child" in md
    assert "## Child heading" in md
    assert image_count == 0
