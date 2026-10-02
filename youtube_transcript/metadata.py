"""Video metadata via yt-dlp (no media download)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import yt_dlp


@dataclass
class VideoMetadata:
    title: str | None
    channel: str | None


def fetch_metadata(video_id: str) -> VideoMetadata:
    """Fetch title and channel name for a video ID. Returns partial data on failure."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    opts: dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception:
        return VideoMetadata(title=None, channel=None)

    if not info:
        return VideoMetadata(title=None, channel=None)

    title = info.get("title")
    channel = info.get("channel") or info.get("uploader")
    return VideoMetadata(
        title=str(title) if title else None,
        channel=str(channel) if channel else None,
    )
