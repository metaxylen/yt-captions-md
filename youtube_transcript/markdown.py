"""Markdown document formatting and caption merging."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CaptionSegment:
    start: float
    text: str


def format_timestamp(seconds: float) -> str:
    total = int(seconds)
    minutes, secs = divmod(total, 60)
    return f"{minutes:02d}:{secs:02d}"


def _normalize_ws(text: str) -> str:
    return " ".join(text.split())


def _dedupe_append(accumulated: str, new_text: str) -> str:
    """Merge caption text while dropping common auto-caption overlaps."""
    new_text = _normalize_ws(new_text)
    if not new_text:
        return accumulated
    if not accumulated:
        return new_text

    acc = accumulated
    acc_lower = acc.lower()
    new_lower = new_text.lower()

    if new_lower == acc_lower or new_lower in acc_lower:
        return acc
    if acc_lower in new_lower:
        return new_text

    # Rolling window: new line repeats the end of the previous chunk
    max_overlap = min(len(acc), len(new_text), 80)
    for size in range(max_overlap, 0, -1):
        if acc[-size:].lower() == new_text[:size].lower():
            rest = new_text[size:].lstrip()
            return f"{acc} {rest}".strip() if rest else acc

    if acc.endswith(("-", "—")):
        return acc[:-1] + new_text
    return f"{acc} {new_text}"


def merge_captions(
    segments: list[CaptionSegment],
    include_timestamps: bool = False,
    pause_threshold: float = 2.0,
    max_paragraph_chars: int = 900,
) -> str:
    """
    Merge caption fragments into paragraphs. Deduplicates overlapping auto captions.
    With include_timestamps, each paragraph starts with [mm:ss] from its first segment.
    """
    if not segments:
        return ""

    paragraphs: list[tuple[float, str]] = []
    para_start = segments[0].start
    current = ""
    prev_start: float | None = None

    for seg in segments:
        text = seg.text.replace("\n", " ")
        if not _normalize_ws(text):
            continue

        gap = 0.0
        if prev_start is not None:
            gap = seg.start - prev_start
        prev_start = seg.start

        new_current = _dedupe_append(current, text) if current else _normalize_ws(text)
        would_break = bool(
            current
            and (gap >= pause_threshold or len(new_current) >= max_paragraph_chars)
        )

        if would_break:
            paragraphs.append((para_start, current.strip()))
            para_start = seg.start
            current = _normalize_ws(text)
        else:
            current = new_current

    if current.strip():
        paragraphs.append((para_start, current.strip()))

    if include_timestamps:
        lines = [f"[{format_timestamp(start)}] {body}" for start, body in paragraphs]
    else:
        lines = [body for _, body in paragraphs]

    return "\n".join(lines)


def build_markdown_document(
    title: str,
    url: str,
    channel: str | None,
    language: str,
    is_generated: bool,
    transcript_body: str,
) -> str:
    cap_type = "auto-generated" if is_generated else "manual"
    channel_line = channel if channel else "—"
    parts = [
        f"# {title}",
        "",
        f"- URL: {url}",
        f"- Channel: {channel_line}",
        f"- Language: {language}",
        f"- Type: {cap_type}",
        "",
        "---",
        "",
        transcript_body,
        "",
    ]
    return "\n".join(parts)
