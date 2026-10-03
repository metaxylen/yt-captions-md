"""CLI: fetch YouTube transcripts and save as Markdown."""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from youtube_transcript.files import resolve_output_path, write_markdown
from youtube_transcript.markdown import build_markdown_document
from youtube_transcript.metadata import fetch_metadata
from youtube_transcript.transcript import TranscriptError, fetch_transcript_with_retry
from youtube_transcript.urls import extract_video_id

DEFAULT_OUTPUT_DIR = Path(
    os.environ.get("YT_CAPTIONS_OUT", "output"),
).expanduser()


@dataclass
class ProcessResult:
    url: str
    success: bool
    message: str
    output_path: Path | None = None


def parse_lang_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def load_urls_from_file(path: Path) -> list[str]:
    urls: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        urls.append(stripped)
    return urls


def process_url(
    url: str,
    output_dir: Path,
    lang_prefs: list[str],
    include_timestamps: bool,
) -> ProcessResult:
    video_id = extract_video_id(url)
    if not video_id:
        return ProcessResult(url=url, success=False, message="invalid YouTube URL")

    try:
        meta = fetch_metadata(video_id)
        transcript = fetch_transcript_with_retry(
            video_id,
            lang_prefs=lang_prefs,
            include_timestamps=include_timestamps,
        )
    except TranscriptError as e:
        return ProcessResult(url=url, success=False, message=e.reason)

    title = meta.title or video_id
    doc = build_markdown_document(
        title=title,
        url=url,
        channel=meta.channel,
        language=transcript.language,
        is_generated=transcript.is_generated,
        transcript_body=transcript.text,
    )
    out_path = resolve_output_path(output_dir, meta.title, video_id)
    write_markdown(out_path, doc)
    return ProcessResult(
        url=url,
        success=True,
        message=str(out_path),
        output_path=out_path,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download YouTube video transcripts and save them as Markdown files.",
    )
    parser.add_argument(
        "urls",
        nargs="*",
        help="One or more YouTube video URLs",
    )
    parser.add_argument(
        "--file",
        "-f",
        type=Path,
        help="Text file with one URL per line (# comments and blank lines ignored)",
    )
    parser.add_argument(
        "--lang",
        type=str,
        default=None,
        help="Comma-separated language codes in preference order (e.g. tr,en)",
    )
    parser.add_argument(
        "--timestamps",
        action="store_true",
        help="Prefix each paragraph with [mm:ss]",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help=(
            "Output directory (default: ./output, or YT_CAPTIONS_OUT if set)"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    urls: list[str] = list(args.urls)
    if args.file:
        if not args.file.is_file():
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            return 1
        urls.extend(load_urls_from_file(args.file))

    if not urls:
        parser.print_help()
        return 1

    lang_prefs = parse_lang_list(args.lang)
    output_dir: Path = args.out if args.out is not None else DEFAULT_OUTPUT_DIR
    results: list[ProcessResult] = []

    for url in urls:
        result = process_url(
            url,
            output_dir=output_dir,
            lang_prefs=lang_prefs,
            include_timestamps=args.timestamps,
        )
        results.append(result)
        if result.success:
            print(f"OK  {url} -> {result.message}")
        else:
            print(f"FAIL {url}: {result.message}", file=sys.stderr)

    succeeded = sum(1 for r in results if r.success)
    failed = len(results) - succeeded
    print()
    print(f"Summary: {succeeded} succeeded, {failed} failed")
    for r in results:
        if not r.success:
            print(f"  - {r.url}: {r.message}")

    return 0 if failed == 0 else 1
