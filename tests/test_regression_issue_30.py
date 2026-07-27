"""Regression test for issue #30: Album cover upload and YouTube URL mode.

This test ensures that ALL functions referenced by inline event handlers
in screen.html are exposed to the window object in screen.js, preventing
regressions where handlers would fail because functions weren't exposed.

The test dynamically parses screen.html for all inline handlers and verifies
each referenced function has a corresponding window.name = name assignment.

Issue: https://github.com/Maestro-Ltd/slopsmith-plugin-tabimport/issues/30
"""

import re
import unittest
from pathlib import Path


class TestIssue30Regression(unittest.TestCase):
    """Ensure all inline event handlers reference exposed window functions."""

    @classmethod
    def setUpClass(cls):
        """Load screen.html and screen.js content for analysis."""
        base_path = Path(__file__).parent.parent

        screen_html_path = base_path / "screen.html"
        if not screen_html_path.exists():
            raise FileNotFoundError(f"screen.html not found at {screen_html_path}")
        with open(screen_html_path, 'r') as f:
            cls.screen_html_content = f.read()

        screen_js_path = base_path / "screen.js"
        if not screen_js_path.exists():
            raise FileNotFoundError(f"screen.js not found at {screen_js_path}")
        with open(screen_js_path, 'r') as f:
            cls.screen_js_content = f.read()

    def _extract_ti_functions_from_inline_handlers(self):
        """Extract all Tab Import functions (ti*) referenced in inline event handlers.

        Returns:
            set: Tab Import function names found in onclick/onchange/ondrop attributes.
        """
        # Extract all inline event handler strings
        inline_pattern = r'on(?:click|change|drop|drag[a-z]*)\s*=\s*"([^"]*)"'
        inline_handlers = re.findall(inline_pattern, self.screen_html_content)

        # Extract Tab Import function names from handler strings
        ti_functions = set()
        for handler in inline_handlers:
            # Extract all function calls like funcName(...) or obj.method(...)
            func_matches = re.findall(r'(?:\w+\.)?(\w+)\s*\(', handler)
            # Keep only Tab Import functions (those starting with 'ti')
            for func in func_matches:
                if func.startswith('ti'):
                    ti_functions.add(func)
        return ti_functions

    def test_all_inline_handlers_are_exposed(self):
        """All Tab Import functions in inline handlers must be exposed to window.

        This is the core regression test: parse screen.html for all inline
        event handlers (onclick, onchange, ondrop, etc.) and verify each
        Tab Import function (ti*) has a corresponding window.name = name assignment.
        """
        # Extract all Tab Import functions from inline handlers
        functions_in_html = self._extract_ti_functions_from_inline_handlers()

        # Extract all window exposures from screen.js
        # Matches: window.funcName = funcName;
        exposure_pattern = r'window\.(\w+)\s*=\s*\1\s*[;,]'
        exposed_functions = set(re.findall(exposure_pattern, self.screen_js_content))

        # Verify every Tab Import inline handler function is exposed
        missing = functions_in_html - exposed_functions
        self.assertFalse(missing,
            f"Tab Import functions in HTML inline handlers but not exposed to window: {missing}\n"
            f"For each function, add to screen.js: window.functionName = functionName;")

    def test_exposure_section_exists(self):
        """Verify the window function exposure section exists."""
        self.assertIn('// Expose functions called from inline HTML event handlers',
                      self.screen_js_content,
                      "Window function exposure section not found")

    def test_no_undefined_custom_handlers_in_html(self):
        """Custom functions (ti*) in inline handlers should be defined.

        This catches typos and accidental references to custom functions that don't exist.
        Built-in browser APIs are not checked here (those are always available).
        """
        # Extract all Tab Import functions from inline handlers
        custom_functions_in_html = self._extract_ti_functions_from_inline_handlers()

        # Extract all function definitions from screen.js
        # Matches: async function name(...) or function name(...)
        definition_pattern = r'(?:async\s+)?function\s+(\w+)\s*\('
        defined_functions = set(re.findall(definition_pattern, self.screen_js_content))

        # Check that every custom inline handler function is defined
        undefined = custom_functions_in_html - defined_functions
        self.assertFalse(undefined,
            f"Inline handlers reference undefined custom functions: {undefined}\n"
            f"Define these in screen.js or check for typos")


if __name__ == '__main__':
    unittest.main()
