import unittest

from youtube_transcript.urls import extract_video_id


class TestExtractVideoId(unittest.TestCase):
    def test_watch_url(self):
        self.assertEqual(
            extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            "dQw4w9WgXcQ",
        )

    def test_watch_with_extra_params(self):
        url = "https://youtube.com/watch?v=dQw4w9WgXcQ&t=42s&list=PLfoo"
        self.assertEqual(extract_video_id(url), "dQw4w9WgXcQ")

    def test_youtu_be(self):
        self.assertEqual(
            extract_video_id("https://youtu.be/dQw4w9WgXcQ"),
            "dQw4w9WgXcQ",
        )

    def test_shorts(self):
        self.assertEqual(
            extract_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ"),
            "dQw4w9WgXcQ",
        )

    def test_bare_id(self):
        self.assertEqual(extract_video_id("dQw4w9WgXcQ"), "dQw4w9WgXcQ")

    def test_invalid(self):
        self.assertIsNone(extract_video_id("https://example.com/watch?v=dQw4w9WgXcQ"))
        self.assertIsNone(extract_video_id("not-a-url"))
        self.assertIsNone(extract_video_id(""))
