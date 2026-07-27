"""Regression test for issue #30: Album cover upload and YouTube URL mode.

This test ensures that required functions are exposed to the window object
in screen.js, preventing a regression where inline event handlers would fail
because the functions were defined but not exposed.

Issue: https://github.com/Maestro-Ltd/slopsmith-plugin-tabimport/issues/30
"""

import re
import unittest
from pathlib import Path


class TestIssue30Regression(unittest.TestCase):
    """Ensure functions needed for album cover and YouTube URL features are exposed."""

    @classmethod
    def setUpClass(cls):
        """Load screen.js content for analysis."""
        screen_js_path = Path(__file__).parent.parent / "screen.js"
        if not screen_js_path.exists():
            raise FileNotFoundError(f"screen.js not found at {screen_js_path}")
        with open(screen_js_path, 'r') as f:
            cls.screen_js_content = f.read()

    def test_cover_image_handler_exposed(self):
        """tiHandleCover must be exposed for album cover upload to work."""
        self.assertIn('window.tiHandleCover', self.screen_js_content,
                      "tiHandleCover not exposed to window object")

    def test_cover_clear_handler_exposed(self):
        """tiClearCover must be exposed for album cover clear button to work."""
        self.assertIn('window.tiClearCover', self.screen_js_content,
                      "tiClearCover not exposed to window object")

    def test_audio_input_mode_exposed(self):
        """tiSetAudioInputMode must be exposed to switch between file and URL modes."""
        self.assertIn('window.tiSetAudioInputMode', self.screen_js_content,
                      "tiSetAudioInputMode not exposed to window object")

    def test_audio_url_handler_exposed(self):
        """tiHandleAudioUrl must be exposed for YouTube URL download to work."""
        self.assertIn('window.tiHandleAudioUrl', self.screen_js_content,
                      "tiHandleAudioUrl not exposed to window object")

    def test_exposure_section_exists(self):
        """Verify the window function exposure section exists."""
        self.assertIn('// Expose functions called from inline HTML event handlers',
                      self.screen_js_content,
                      "Window function exposure section not found")

    def test_inline_handlers_can_call_cover_functions(self):
        """HTML event handlers referencing cover functions should work."""
        # Verify that the HTML would call these functions
        self.assertIn('tiHandleCover', self.screen_js_content,
                      "tiHandleCover function definition required")
        self.assertIn('tiClearCover', self.screen_js_content,
                      "tiClearCover function definition required")

    def test_inline_handlers_can_call_audio_url_functions(self):
        """HTML event handlers referencing audio URL functions should work."""
        self.assertIn('tiSetAudioInputMode', self.screen_js_content,
                      "tiSetAudioInputMode function definition required")
        self.assertIn('tiHandleAudioUrl', self.screen_js_content,
                      "tiHandleAudioUrl function definition required")


if __name__ == '__main__':
    unittest.main()
