# Task 17 senior review: photo preview and selection races

Branch `claude/photo-preview-17-senior` from main 4e626f9. Junior branch `antigravity/photo-preview-17` at 6796e563eca02d6b81507f6fc769fa9834cffbf0 reviewed, not merged.
No classification, vocabulary or data change: only `web_preview/template.html` among source files; parity 921/921 identical; full suite 2364 passed, 5 xfailed.

## Reproduced (delayed promises; `tests/js/photo_races_17.js`)
Thumbnail decode and text reader are held on promises released by hand; images are generated in the page. Not a native file-picker test and not real OCR.

| Case | main 4e626f9 | junior 6796e56 | this branch |
|---|---|---|---|
| Thumbnail pending, photo replaced | B shown (guarded by token) | same | same |
| Thumbnail pending, cleared by empty change | stays hidden | stays hidden | stays hidden |
| Thumbnail pending, input emptied + `cancel` event | no handler: preview A stays, input empty, button enabled | **preview A returns, button disabled** (cancel does not bump the token) | hidden, button disabled |
| Photo replaced during first reading | reading continues, second pass opens B, A's result rendered with "Done" | same | reading stopped, reader terminated, no result |
| Photo replaced during second pass | A's result rendered for B | same | no result |
| Photo cleared during first reading | `prepare(null)` throws, failure card, Read button enabled with no file | same | no card, button disabled |
| Finished result, then another photo chosen | A's result stays next to B | cleared (clears every result, incl. paste results) | cleared only when it came from the photo path |
| Synthetic `cancel` with selection intact | no-op | clears selection | no-op |

The independent repro of the first two junior-state rows (actual 81439-byte image, delayed `onload`, mocked OCR) matches.

## Changes kept from the junior branch
- CSS for `#photo-preview` (`object-fit: contain`, `image-orientation: from-image`).
- `makeThumb` guards: null file, zero-size image, missing 2d context, `clearTimeout`.
- Token-guarded `img.onerror`.

## Not kept
- `click` handler that empties the input value: not a demonstrated defect; it clears the selection when the picker only opens while `photoFile` stays set, and it is the reason the junior cancel handler had to clear state.
- `clearResults()` on every selection: also wiped paste-tab results; replaced by clearing only photo-derived content.
- "Loading preview…" status text; Windows-only tests, screenshots and `evaluation/photo_preview_17/*`.

## Fix (template.html)
- `applySelection(file)`: single path for change/cancel; bumps `previewToken`, stops the active reading, removes a photo-derived result, sets the button from the file.
- `cancel`: re-syncs to `input.files`; nothing changes if it still holds the photo in use (native cancel semantics differ by browser; synthetic events are harmless).
- The reading captures `file` at click; all passes (`prepare`, flat, rotations) use it; `over` is checked after every await including `prepare` and `createWorker`; the stopped run renders nothing and shows no failure card.

## Revision 2 (independent review of 91e9a38)
Two further defects, both reproduced on 91e9a38 with a delayed `terminate()` promise / held image decode (`tests/js/photo_races_17.js`, T9-T11):
- Final cleanup: the success path set `over = true; activeRun = null` before `await worker.terminate()`, so a cancel or replacement during that await found no cancellable run; the old run then resumed and wrote its NOVA card, "Done" and the OCR text into the Paste tab (reproduced for cancel and for replace).
- Second pass: `recognize(await prepare(...))` could start the reader on an already terminated worker when the photo was replaced during preparation (`ocrCalls` 2 on 91e9a38).
Fix: the run stays cancellable across the terminate await and is finished (`over`, `activeRun = null`) only after it, and only if still current; `prepare` and `recognize` are separate awaits with an `over` check between them (second pass and rotation retries). Rotations are off (`ROTATIONS` empty), so that branch has the same code change but no UI test. After the fix: ocrCalls 1, no result, no status "Done", Paste text unchanged.

## Tests
`tests/test_photo_races_17.py` (10 tests, skip when node/playwright/dist are missing; no platform-specific browser or image path). `tests/test_photo_preview.py` unchanged and passing.

## Unresolved
Original root cause of the owner's failed preview is not established: the owner's failed preview used the actual 81439-byte original, and it works locally. High-resolution mobile memory is not claimed.

## Deployment note (separate request)
Production at 433 rows/859 parity: the build of 4e626f9 passes locally (509 rows, parity 921/921) and `web_preview/dist/` is gitignored and built at deploy time, so no tracked asset update is needed. The owner's dashboard check found the manual deploy of 4e626f9 refused by the free-plan daily API-deployment cap (`api-deployments-free-per-day`, over 100 per day). Retry is arranged by the owner after the cap resets; nothing was triggered from here.
