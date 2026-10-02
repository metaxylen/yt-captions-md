"""Transcript fetching with retries and caption selection."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Sequence

from youtube_transcript_api import (
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    RequestBlocked,
    TranscriptsDisabled,
    VideoUnavailable,
    YouTubeRequestFailed,
    YouTubeTranscriptApi,
)

from youtube_transcript.markdown import CaptionSegment, merge_captions


class TranscriptError(Exception):
    """User-facing transcript failure."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


@dataclass
class FetchedTranscript:
    language: str
    is_generated: bool
    text: str


def _match_lang(language_code: str, lang: str) -> bool:
    return language_code == lang or language_code.startswith(f"{lang}-")


def _select_transcript(transcript_list, lang_prefs: Sequence[str]):
    """Prefer manual captions in lang order, then auto, then any available."""
    transcripts = list(transcript_list)
    manual = [t for t in transcripts if not t.is_generated]
    generated = [t for t in transcripts if t.is_generated]

    if lang_prefs:
        for lang in lang_prefs:
            for t in manual:
                if _match_lang(t.language_code, lang):
                    return t
        for lang in lang_prefs:
            for t in generated:
                if _match_lang(t.language_code, lang):
                    return t

    if manual:
        return manual[0]
    if generated:
        return generated[0]
    return None


def _map_could_not_retrieve(exc: CouldNotRetrieveTranscript) -> TranscriptError:
    if isinstance(exc, TranscriptsDisabled):
        return TranscriptError("captions are disabled for this video")
    if isinstance(exc, VideoUnavailable):
        return TranscriptError("video is private or unavailable")
    if isinstance(exc, NoTranscriptFound):
        return TranscriptError("no transcript available for this video")
    return TranscriptError(f"could not retrieve transcript: {exc}")


def fetch_transcript_with_retry(
    video_id: str,
    lang_prefs: Sequence[str],
    include_timestamps: bool,
    max_retries: int = 3,
    sleep_fn: Callable[[float], None] = time.sleep,
    api: YouTubeTranscriptApi | None = None,
) -> FetchedTranscript:
    client = api or YouTubeTranscriptApi()
    last_error: Exception | None = None

    for attempt in range(max_retries):
        try:
            transcript_list = client.list(video_id)
            chosen = _select_transcript(transcript_list, lang_prefs)
            if chosen is None:
                raise TranscriptError("no transcript available for this video")

            fetched = chosen.fetch()
            segments = [
                CaptionSegment(start=float(s.start), text=str(s.text or ""))
                for s in fetched
            ]
            body = merge_captions(segments, include_timestamps=include_timestamps)
            return FetchedTranscript(
                language=fetched.language_code,
                is_generated=fetched.is_generated,
                text=body,
            )
        except TranscriptError:
            raise
        except CouldNotRetrieveTranscript as e:
            raise _map_could_not_retrieve(e)
        except (YouTubeRequestFailed, RequestBlocked) as e:
            last_error = e
            if attempt < max_retries - 1:
                sleep_fn(2 ** attempt)
                continue
            raise TranscriptError(f"network or rate limit error after retries: {e}")
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                sleep_fn(2 ** attempt)
                continue
            raise TranscriptError(f"unexpected error: {e}")

    raise TranscriptError(f"failed after retries: {last_error}")
