"""YouTube URL parsing and video ID extraction."""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

_VIDEO_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{11}$")

_HOST_PATTERNS = (
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
    "www.youtu.be",
)


def extract_video_id(url: str) -> str | None:
    """
    Extract an 11-character YouTube video ID from a URL or bare ID string.
    Returns None if the input is not a valid YouTube video reference.
    """
    raw = url.strip()
    if not raw:
        return None

    if _VIDEO_ID_PATTERN.match(raw):
        return raw

    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw

    try:
        parsed = urlparse(raw)
    except ValueError:
        return None

    host = (parsed.netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]

    if not any(host == h or host.endswith("." + h) for h in _HOST_PATTERNS):
        return None

    path = parsed.path or ""

    if host in ("youtu.be", "www.youtu.be"):
        segment = path.lstrip("/").split("/")[0]
        if _VIDEO_ID_PATTERN.match(segment):
            return segment
        return None

    if path.startswith("/shorts/"):
        segment = path.split("/")[2] if len(path.split("/")) > 2 else ""
        if _VIDEO_ID_PATTERN.match(segment):
            return segment
        return None

    if path.startswith("/watch"):
        query = parse_qs(parsed.query)
        vid = query.get("v", [None])[0]
        if vid and _VIDEO_ID_PATTERN.match(vid):
            return vid
        return None

    if path.startswith("/embed/"):
        segment = path.split("/")[2] if len(path.split("/")) > 2 else ""
        if _VIDEO_ID_PATTERN.match(segment):
            return segment
        return None

    if path.startswith("/v/"):
        segment = path.split("/")[2] if len(path.split("/")) > 2 else ""
        if _VIDEO_ID_PATTERN.match(segment):
            return segment

    return None
