import unittest

from youtube_transcript.markdown import CaptionSegment, merge_captions


class TestMergeCaptions(unittest.TestCase):
    def test_merges_into_paragraphs(self):
        segments = [
            CaptionSegment(0.0, "Hello"),
            CaptionSegment(0.5, "world."),
            CaptionSegment(5.0, "New paragraph here."),
        ]
        text = merge_captions(segments, include_timestamps=False, pause_threshold=2.0)
        self.assertEqual(text, "Hello world.\nNew paragraph here.")

    def test_dedupes_overlap(self):
        segments = [
            CaptionSegment(0.0, "the quick brown"),
            CaptionSegment(1.0, "brown fox jumps"),
        ]
        text = merge_captions(segments)
        self.assertEqual(text, "the quick brown fox jumps")

    def test_timestamps(self):
        segments = [
            CaptionSegment(65.0, "One"),
            CaptionSegment(66.0, "two."),
        ]
        text = merge_captions(segments, include_timestamps=True)
        self.assertTrue(text.startswith("[01:05] One two."))

    def test_skips_duplicate_line(self):
        segments = [
            CaptionSegment(0.0, "same line"),
            CaptionSegment(1.0, "same line"),
        ]
        text = merge_captions(segments)
        self.assertEqual(text, "same line")
