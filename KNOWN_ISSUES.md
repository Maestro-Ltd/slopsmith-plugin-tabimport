# Known UI Issues — Tab Import

Findings from a frontend UI-bug audit of `screen.html`/`screen.js` (2026-07-22, 32.6KB, no `assets/*.js`/`*.css`, no `settings.html`). Ranked by severity/confidence. No code changes have been made — this is a catalog for follow-up work.

## 1. Five inline event handlers reference functions never exposed on `window` (Critical) — ✅ FIXED

**Status:** Fixed in PR #30 (commit 3513c6e). Regression test added to prevent recurrence.

`screen.js` wraps everything in `(function(){'use strict'; ... })();` for scope isolation. Functions declared inside are invisible to inline `onclick`/`onchange` attributes unless explicitly assigned to `window`. The exposure list at the end of `screen.js` was missing:

- `tiHandleCover` — `screen.html:42` (album-cover file input `onchange`)
- `tiClearCover` — `screen.html:44` ("Remove" cover button)
- `tiSetAudioInputMode` — `screen.html:90,92` ("Upload File" / "YouTube URL" toggle)
- `tiHandleAudioUrl` — `screen.html:125` ("Download Audio" button)
- `tiMergePair` — dynamically generated, `screen.js:615` (each piano-pair row's "Merge" button)

**What was broken:** Album-cover upload, YouTube-audio-URL flow, piano LH/RH merge action.

**How it was fixed:** Added missing function exposures to the window object and created `tests/test_regression_issue_30.py` to prevent this regression.

**See also:** [CLAUDE.md — Inline Event Handlers Require Window Exposure](CLAUDE.md#1-inline-event-handlers-require-window-exposure)

## 2. Piano LH/RH merge section never populated on initial screen load (High)

`tiLoadPianoPairs()` (`screen.js:597`) is the only thing that fetches `/piano-pairs` and shows `#ti-piano-merge-section`, but it's only called from `tiReset()` (`screen.js:592`), itself only invoked from error/"Try again"/"Import Another" buttons.

**Failure scenario:** A user who opens "Import Tab" purely to merge existing piano hands (not to import anything new) sees an empty screen forever — the section only appears after completing or failing at least one GP import first, and even then its Merge button is broken by issue #1.

## 3. No `ws.onclose` handler on the build WebSocket (High)

`screen.js:507-533` wires `ws.onmessage` and `ws.onerror` only.

**Failure scenario:** If the backend closes the socket cleanly (unhandled server exception, timeout, container restart) without sending an `error`/`done` frame, and without the browser firing a WS `error` event, the progress bar/stage text freezes indefinitely with no failure indication and no retry affordance — the user's only recourse is navigating away and losing their track/audio selections.

## 4. Race condition on the main drop zone during upload (High)

`screen.js:36-54` binds `click`/`dragover`/`drop` listeners directly to `#ti-dropzone`; `tiHandleFile` (`screen.js:58-98`) only replaces the element's `innerHTML` with a "Parsing…" message — it doesn't disable or unbind the listeners.

**Failure scenario:** Dropping/selecting a second `.gp*` file before the first `/upload` fetch resolves fires a second concurrent `tiHandleFile` call. Whichever `fetch` resolves last silently overwrites the shared `_tiTmpPath`/`_tiHasEmbedded`/`_tiRequiresAudio` globals and repaints the parsed-track UI — the title/tracks shown on screen can end up not matching the file that actually gets built.

## 5. Same missing in-flight guard on the audio drop target (Medium)

`screen.js:297-347` / `screen.html:96-107` — `tiHandleAudioFile` replaces `#ti-audio-drop`'s children with "Loading…" but the drop target's `onclick`/`ondrop` attributes stay live, racing on `_tiAudioB64`/`_tiAudioFilename` the same way as #4.

## 6. "Download Audio" has no disable-while-downloading guard (Medium)

`screen.html:125` / `screen.js:255-293`. Independent of issue #1 (currently unreachable): no button-disable or request-dedup — repeated clicks would fire concurrent `/youtube-audio` POSTs, with only a static "Downloading audio…" string as feedback and no cancellation.

## 7. Fragile DOM coupling for the Build-button gate (Medium)

`tiUpdateBuildButton` (`screen.js:166`) finds the Build button via `document.querySelector('button[onclick="tiBuild()"]')` — a literal-string match against `screen.html:142`'s inline `onclick` attribute.

**Failure scenario:** If that attribute's exact text ever changes, `querySelector` returns `null`, the early `if (!btn) return` swallows it silently, and the "audio required for GP6/7/8" disabled-state/tooltip gating stops working with no error — a build could proceed for a format that's supposed to be blocked.

## 8. No progress feedback during initial GP parse (Low)

`tiHandleFile` (`screen.js:67`) shows only a static `"Parsing {filename}..."` string, unlike the build step which has a real progress bar. A slow server-side parse of a large multi-track GP8 file is indistinguishable from a hang.

## 9. `esc()` misapplied to a plain-text `alert()` sink (Low/cosmetic)

`screen.js:322` — `alert(\`Unsupported audio format (.${esc(ext)})...\`)` HTML-escapes a string going into a plain `alert()`, not `innerHTML`. Harmless, but an extension containing `&`/`<`/`'` would display its escaped entity form literally in the alert instead of the raw character.

---

*Verified clean:* this plugin is unusually careful about XSS — a local `esc()` helper (`screen.js:20-27`) consistently escapes every user/server-supplied string before `innerHTML` assignment. The one raw interpolation (`<img src="${e.target.result}">` for cover art, `screen.js:385`) is a browser-generated base64 `data:` URI from the user's own local file selection, not attacker-controllable. No UI implies GP-import features that aren't supported (no difficulty slider, no per-string finger diagrams). No arbitrary-value Tailwind classes, so no missing `styles` manifest concern.
