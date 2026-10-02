"""Filename sanitization and Markdown file output."""

from __future__ import annotations

import re
from pathlib import Path

_ILLEGAL_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_WHITESPACE = re.compile(r"\s+")


def sanitize_filename(title: str, max_length: int = 200) -> str:
    """Strip characters illegal on common filesystems and collapse whitespace."""
    name = _ILLEGAL_FILENAME_CHARS.sub("", title)
    name = _WHITESPACE.sub(" ", name).strip(" .")
    if not name:
        return ""
    if len(name) > max_length:
        name = name[:max_length].rstrip(" .")
    return name


def resolve_output_path(
    output_dir: Path,
    title: str | None,
    video_id: str,
) -> Path:
    """
    Choose a .md path under output_dir. Uses sanitized title or video_id.
    If the file exists, append the video ID before the extension.
    """
    base = sanitize_filename(title or "") or video_id
    candidate = output_dir / f"{base}.md"
    if candidate.exists():
        suffix_id = sanitize_filename(f"{base} {video_id}") or video_id
        candidate = output_dir / f"{suffix_id}.md"
    return candidate


def write_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
