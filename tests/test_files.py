import tempfile
import unittest
from pathlib import Path

from youtube_transcript.files import resolve_output_path, sanitize_filename


class TestSanitizeFilename(unittest.TestCase):
    def test_strips_illegal_chars(self):
        self.assertEqual(sanitize_filename('Hello: World? "Test"'), "Hello World Test")

    def test_collapses_whitespace(self):
        self.assertEqual(sanitize_filename("  foo   bar  "), "foo bar")

    def test_empty_after_strip(self):
        self.assertEqual(sanitize_filename('<>:"/\\|?*'), "")


class TestResolveOutputPath(unittest.TestCase):
    def test_uses_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = resolve_output_path(Path(tmp), "My Video", "abc12345678")
            self.assertEqual(out.name, "My Video.md")

    def test_falls_back_to_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = resolve_output_path(Path(tmp), None, "dQw4w9WgXcQ")
            self.assertEqual(out.name, "dQw4w9WgXcQ.md")

    def test_collision_appends_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = root / "My Video.md"
            existing.write_text("old", encoding="utf-8")
            out = resolve_output_path(root, "My Video", "dQw4w9WgXcQ")
            self.assertEqual(out.name, "My Video dQw4w9WgXcQ.md")
