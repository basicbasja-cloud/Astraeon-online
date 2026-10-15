# Exact file map

Paths in this document start at the repository root. See [FILES.csv](FILES.csv) / [FILES.json](FILES.json) for each retained file's SHA-256 and bytes, [ALL-CASES.md](ALL-CASES.md) for every case entry, and [TOOLS.csv](TOOLS.csv) for Python tools and statically declared CLI arguments. The inventory excludes itself and late verification receipts to avoid self-hash loops. It indexes tracked research/skill files plus current delivery, not credentials or unrelated game files.

## Current painted delivery — `research/sprite-animation/paintover-handoff-v46/`

| Path below this case | What it is / how to use it |
|---|---|
| `raw/{S,SE,E,NE,N,NW,W,SW}-attempt1.png` | Native unmodified 1536×1024 RGBA strips; 4 columns × 2 rows; never overwrite |
| `inputs/{view}-pose.png` | Exact v45 review poses assembled on the same 4×2 grid |
| `inputs/{view}-owners.png` | Source diagnostic ownership: BLUE anatomical RIGHT, ORANGE LEFT, green head; not an image detector |
| `input-manifest.json` | Hash-bound input guide provenance and accepted-style scope |
| `prompts/{view}.json` | Exact saved instructions/references for that host generation job |
| `generation-ledger.json` | Original local provider path, retained raw copy/hash, tool kind and billing visibility limits |
| `frames/{view}/00.png` … `07.png` | Exact 384×512 cell crops, no per-frame geometry correction |
| `previews/{view}.gif` | Eight drawings on the disclosed source review clock |
| `previews/{view}-source-vs-painted.gif` | Shared-clock source left / actual paint right; same cell size, no matching-by-fit |
| `previews/eight-directions.gif` | Eight-facing overview on one clock |
| `previews/all-frames.png` | All 64 frames for visual review; labels outside art |
| `editor/{view}.ora` | Free Krita/GIMP-compatible full art layer + hidden source and owner layers |
| `review.html` | Portable embedded-image grid/step/play review; no server or network needed |
| `paint-review.json` | Alpha/component/bounds and neutral-return observations, not semantic anatomy |
| `manual-observations.json` | SHA-bound visual findings and still-unknown items |
| `build-delivery.py` | Rebuild derived PNG/GIF/ORA/viewer and measurements from retained raws; no generation |
| `index-handoff.py` | Static file/tool/case inventory; never executes historical authoring scripts |
| `verify-handoff.py` | Read-only integrity/link check |
| `handoff/` | Complete transfer documents, inventories and verification evidence |

## Rig source and repair — `research/sprite-animation/left-arm-repair-v45/`

| File or directory | Purpose |
|---|---|
| `original-character.blend` | Current working skinned model, corrected LEFT arm, pickup animation; open in Blender 4.3.2 |
| `build-character.py` | Original procedural build/targets/rig code; inspect before copying into a new case |
| `arm-contract.json`, `inspect-arm.py`, `arm-inspection.json` | Source chain thresholds, actual saved dense evaluations and before/after findings |
| `display-bind.json`, `preview-bindings.json`, `receipt.json` | Fixed render/display transforms, clocks and retained-source provenance |
| `renders/`, `review/key/`, `review/ownership/` | Actual captured source pixels and eight-key guides |
| `arm-visibility/`, `before-arm-visibility/` | Depth-tested vs isolated arm references; invisible anatomy stays UNKNOWN |
| `left-arm-before-after.png`, `isolated-left-before-after.png`, `before-after-eight.gif` | Visible and isolated repair comparisons |
| `failed-isolation-prop-REJECTED/` | Real failure: animated gem appeared in isolated pass; retain as regression |
| `audit.py`, `audit.json`, `test-arm-gate.py`, `regressions.json` | Case-specific source audit and negative controls; do not rerun here in place |
| `review.html`, `browser-check.cjs`, `browser-qa.json` | Source viewer and its offline browser evidence |
| `evidence-manifest.json` | Frozen SHA-bound leaves |
| `README.md`, `KNOW-HOW.md`, `NEXT.md` | Detailed design and remaining limitations |

## Approved art, modular history, reference sources

* `research/sprite-animation/recovery-key-v39/`: accepted one-view pickup, body/head/collar render banks and complete GIFs. Inspect `README.md`, contracts and evidence manifest before reusing transforms. This is the positive style reference for v46.
* `research/sprite-animation/rear-motion-v40/user-v39-acceptance.json`: authoritative recorded scope of the user's acceptance. v40's own rear motion is rejected.
* `research/sprite-animation/registered-walk-attack-v21/walk/W/`: accepted protected W walk; attacks in this case are rejected.
* `research/sprite-animation/joint-tracking-ro-v30/protected-W.json`: exact protected W bytes; `preset-source/`: creator-licensed KayKit 23-joint source banks; `new-preset-samples.json.gz`: actual sampled world-joint evidence.
* `research/sprite-animation/continuous-arm-v43/source/source.json`: camera/core target dependency used by v45 authoring. `reference/`: acquired CMU ASF/AMC/video; source/image owner failure evidence is preserved separately.
* `research/sprite-animation/free-character-v44/`: original free procedural character, skinning and corrective GLB experiment. Read that case's README before using any GLB.
* `research/sprite-animation/rpg-motion-foundation-v29/`: broad source catalog, 99 motion recipes, actual retrieval receipts, open presets/sprite boards and paper notes.
* `skills/modular-eight-direction-sprites/SKILL.md`: reusable pipeline skill; `references/`: method notes; `scripts/`: reusable diagnostics and regression fixtures. This skill still has historical sections; current entry is v46 handoff.

Historical root research README is not the current status authority. Old character experiments remain evidence of failures, not a positive style dataset.

Actual decoded artifact check: `python research/sprite-animation/paintover-handoff-v46/check-artifacts.py` verifies every crop and guide against original bytes, GIF exposure clock and ORA painted layer. It does not modify files or approve art. Exact native generation prompts are retained in `prompts/{view}-exact.txt`; JSON alongside records the reference order and metadata.
