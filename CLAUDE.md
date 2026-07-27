# Tab Import Plugin — Development Guidelines

## Project Overview

Tab Import is a Slopsmith plugin for importing Guitar Pro files and converting them to playable CDLC. The UI is built with vanilla JavaScript in an IIFE (Immediately Invoked Function Expression) for scope isolation.

**Key files:**
- `screen.html` — UI markup with inline event handlers
- `screen.js` — Plugin logic (wrapped in IIFE for scope isolation)
- `routes.py` — Backend API endpoints
- `tests/` — Regression tests and unit tests
- `KNOWN_ISSUES.md` — Documented UI bugs awaiting fixes

## Architecture Decisions

### IIFE Scope Isolation

All JavaScript is wrapped in `(function() { 'use strict'; ... })();` to prevent global namespace pollution. This means **functions are private by default** and must be explicitly exposed to the `window` object if they need to be called from HTML inline event handlers.

**Important:** When adding new features that use inline event handlers, the corresponding functions MUST be added to the window exposure list at the end of `screen.js`.

## Critical Development Rules

### 1. Inline Event Handlers Require Window Exposure

**Rule:** If you reference a function in an inline event handler (`onclick`, `onchange`, `ondrop`, etc.) in `screen.html`, that function MUST be exposed to `window` in `screen.js`.

**Example:**
```html
<!-- In screen.html -->
<input type="file" onchange="tiHandleCover(this.files[0])">
<button onclick="tiClearCover()">Remove</button>
```

```javascript
// At end of screen.js (before closing IIFE)
window.tiHandleCover = tiHandleCover;
window.tiClearCover = tiClearCover;
```

### 2. Test Window Exposures Before Committing

Always run the regression test before pushing:
```bash
python -m unittest tests.test_regression_issue_30 -v
```

This catches missing function exposures immediately.

### 3. Consider Event Delegation Over Inline Handlers

Inline event handlers create a maintenance burden (remember to expose functions). Consider using event delegation instead:

**Before (requires window exposure):**
```html
<button onclick="tiHandleCover()">Upload</button>
```

**After (no exposure needed):**
```html
<button id="ti-cover-upload" class="ti-handler" data-action="cover">Upload</button>
```

```javascript
document.addEventListener('click', (e) => {
    if (e.target.id === 'ti-cover-upload') tiHandleCover();
});
```

### 4. Regression Test Requirements

When fixing a bug or adding a feature that touches `screen.js`/`screen.html`:
- Add a test to `tests/test_regression_issue_30.py` if it's about function exposure
- Add a unit test if it's about business logic
- Run all tests: `python -m unittest discover tests -v`

## Common Pitfalls

### ❌ Adding HTML with inline handlers but forgetting function exposure
```html
<!-- BAD: This function won't be callable -->
<button onclick="tiNewFeature()">Click me</button>
```

→ Always check both HTML changes AND JavaScript exposures in the same PR.

### ❌ Manually listing functions instead of systematically checking
When wrapping code in an IIFE, don't guess which functions to expose — search the HTML for all inline handlers and match them to functions.

```bash
# Quick check: find all inline handler functions
grep -oE 'on(click|change|drop)="[^"]*' screen.html | grep -oE '[a-zA-Z_][a-zA-Z0-9_]*\(' | sort -u
```

### ❌ Forgetting to test after refactoring
If you touch the IIFE or function exposures, test the UI in a browser:
1. Try album cover upload
2. Try switching to YouTube URL mode
3. Try the piano LH/RH merge feature

## Testing Strategy

### Automated Tests
- `tests/test_regression_issue_30.py` — Verifies all inline handlers are exposed
- `tests/test_auto_select_tracks.py` — Backend track selection logic (skipped if gp2rs unavailable)

### Manual Testing Checklist
Before marking a PR ready:
- [ ] Upload a .gp file successfully
- [ ] Select tracks and arrangements
- [ ] Upload an album cover image (checks `tiHandleCover` exposed)
- [ ] Switch to YouTube URL mode (checks `tiSetAudioInputMode` exposed)
- [ ] Attempt YouTube audio download (checks `tiHandleAudioUrl` exposed)
- [ ] Build a CDLC with audio sync
- [ ] Verify progress bar works end-to-end

## Related Issues

See `KNOWN_ISSUES.md` for documented UI bugs. Priority fixes:

| Issue | Status | Notes |
|-------|--------|-------|
| #1 — Five inline handlers missing window exposure | **FIXED** (PR #30) | Regression test added to prevent recurrence |
| #2 — Piano merge section not loaded on init | Open | Calls `tiLoadPianoPairs()` on screen init, not just after reset |
| #3 — No `ws.onclose` handler on build socket | Open | Add close handler to catch network errors |
| #4 — Race condition on main drop zone | Open | Disable listeners during upload in progress |

## Code Review Checklist for Maintainers

When reviewing PRs that touch `screen.html` or `screen.js`:

- [ ] Do new HTML inline event handlers have corresponding functions in screen.js?
- [ ] Are those functions added to the window exposure list at the end of screen.js?
- [ ] Does the regression test still pass? (`python -m unittest tests.test_regression_issue_30 -v`)
- [ ] Have all tests been run? (`python -m unittest discover tests -v`)
- [ ] Have you manually tested the affected features in a browser?
- [ ] Is there a test case for the new functionality?

## Resources

- [KNOWN_ISSUES.md](KNOWN_ISSUES.md) — Documented UI bugs
- [README.md](README.md) — User-facing feature documentation
- GitHub Issues — Feature requests and bug reports
