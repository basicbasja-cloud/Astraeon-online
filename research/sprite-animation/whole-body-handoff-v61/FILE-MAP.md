# File map and reading order

Paths in this document are relative to this case unless marked **repository root**. The [machine inventory](FILE-INVENTORY.tsv) lists every snapshot file and its size. The SHA manifest covers all case payloads except itself.

## Entrypoints

| File | Purpose / authority |
| --- | --- |
| [handoff/00-START.md](handoff/00-START.md) | Full user intent, scope, constraints, results, blocker diagnosis and ordered next work. Read first. |
| [STATUS.json](STATUS.json) |48 source clip records with exact baseline hashes/clocks, current candidate pointers and next gate. All production flags false. |
| [README.md](README.md) | Embedded9 GIFs, review status and transfer overview. |
| [REPRODUCE.md](REPRODUCE.md) | Read-only check, offline players, native files, scratch restore and supported CLI examples. |
| [KNOW-HOW.md](KNOW-HOW.md) | Failures and why previous proxies were insufficient. |
| [REFERENCES.md](REFERENCES.md) | External RO research, pinned tooling, billing/authorization boundary. |
| [RELOCATION.json](RELOCATION.json) | Original checkout prefix,30 raw UUID→preserved job mappings, omitted duplicate payload policy. |
| [restore-workspace.py](restore-workspace.py) | Fresh scratch only; copies/rebases retained inputs and reconstructs omitted repeated timeline PNGs by exact hash. |
| [verify-handoff.py](verify-handoff.py) | Read-only hashes,48 non-production statuses, clip clocks/keys, layer recomposition and preserved failure checks. |
| [TRANSFER-VALIDATION.json](TRANSFER-VALIDATION.json) | Actual transfer-specific verification evidence, distinct from earlier live tool receipts. |
| [evidence-manifest.json](evidence-manifest.json) | SHA256/byte counts of every transferred case file. Not art acceptance. |

## Source, guides and generation

| Path | Contents / use |
| --- | --- |
| `snapshot/matrix.json`, `audit-matrix.py` | Initial48clip/964exposure provenance audit. Current STATUS supersedes acceptance interpretation. |
| `snapshot/static-review.jpg`, `moving-midpoints.jpg` | Actually inspected source boards; old segmented shape remains rejected. |
| `snapshot/generation/generation-ledger.json` |30 imagegen jobs, prompts, raw outputs, reference order/hashes and decisions. Latest head discovery supersedes earlier complete-head labels. |
| `snapshot/generation/raw/job01.png`…`job30.png` | Exact raw generated originals, including rejected jobs. No repaint or image optimization. |
| `snapshot/generation/prompts/job01.txt`…`job30.txt` | Exact generation prompts. Named prompt files also retained. |
| `snapshot/generation/job-ids.json` | Indexed prompt variable / image UUID map. |
| `snapshot/generation/*-layout.png`, `*-poses-guide.png` | Original style authorities and pose-only layouts for pickup/ready/walk. Do not promote segmented guide pixels to final body. |
| `snapshot/generation/*-walk-RO-large-guide.png`, `RO-guide-family.json` | External RO phase guides and common scale/translation provenance. Reference only. |
| `snapshot/generation/S-walk-leftstep-guide.png/.json` | Explicit GUIDE ONLY lower-leg reflection for native redraw job29; not a mirrored final character. |
| `snapshot/generation/*.py` | Original iteration/import/guide helpers, retained verbatim for provenance. Some require omitted failed intermediates; do not blindly run in place. `ledger.py` is stale23-job builder. |
| `snapshot/generation/ase-file-specs.md`, `ase-file-specs-source.json` | Public native format text and retrieval/hash provenance. |

## Selected candidate directories

All names below live in `snapshot/generation/`. `keys/` contains8 exact full-canvas drawings. `clip.json` is authoritative timing and frame hashes. `review/preview.gif` and `contact-sheet.png` are review artifacts. Pickup `frames/` is complete16 exposures; ready/walk repeated timeline PNGs are deliberately omitted and restored by exact key digest. Selected files remain candidates, not final approvals.

| Directory | Primary evidence / exact final technical branch |
| --- | --- |
| `S-candidate7/` | `motion-review.json`, `contact-review.json`, extraction policy, `four-slots2.json`, `head-extraction3/{body,head,mask}/`, `layer-player2/review.html`, `native-editable2/pickup-four-slots.aseprite`, `native-format2/sprite.aseprite`, `native-roundtrip-review.json`, native-format2/package-review.json. |
| `W-candidate2/` | Same motion/contact/source pattern, `head-extraction4/`, `four-slots2.json`, `layer-player/review.html`, `native-editable2/pickup-four-slots.aseprite`, native-roundtrip-review. Hidden second sole unproved. |
| `E-candidate1/` | `head-extraction3/`, `four-slots2.json`, `layer-player/review.html`, `native-editable3/pickup-four-slots.aseprite`, native-roundtrip-review. Native-editable2 timeout negative retained as receipt only. |
| `S-ready-candidate2/` | import/contact, keys,24-exposure clip, GIF/board; canonical-prototype.jpg and original/source-head-coordinates.jpg explain head reuse experiment. Crown1/1. |
| `W-ready-candidate1/` | import/contact, keys,24-exposure clip, GIF/board. Crown6/3; full acceptance pending. |
| `N-ready-candidate1/` | import/contact, keys, GIF/board. Crown10/6 FAIL. Job30 new redraw only in raw/job30.png, unreviewed. |
| `E-ready-candidate1/` | import/contact, keys, GIF/board. Crown8/6 FAIL. |
| `S-walk-candidate1/` | import/source selection, keys,80-exposure clip, GIF/board. Job27+29, crown pass, full gait/head QA pending. |
| `W-walk-candidate1/` | import/source selection, keys,80-exposure clip, GIF/board. Job21+22, crown pass, phase/head QA pending. |

## Head blocker / negative evidence

| Path | Why it matters |
| --- | --- |
| `snapshot/generation/S-head-fields.json`, `S-head-fields2.json` | First and stricter authored ownership contracts; full source hash-bound. |
| `snapshot/generation/S-head-fields*/ownership-review.json` | Broader initial ROI false confidence versus stricter second-contract real fringe FAIL. All source RGBA remains intact. |
| `snapshot/generation/S-head-fields*/{head,body,mask}/` |9 masks each: original S then8 ready keys. These are rejected ownership drafts. |
| `snapshot/generation/S-head-field-detail.jpg` | Enlarged canonical/source/composite/model comparison; visible collar-fragment issue. |
| `snapshot/static-head-extraction/` |16 historical idle/sit splits. Canonical originals lose opaque fringe ownership; not accepted reusable heads. |
| `snapshot/tool-extraction/`, `head-tool-tests.json`, `check-head-tool.py` |16 mask-tool controls and original v58 technically exact splits. Art still rejected. Some original nuisance-mask test dependencies are archival only. |
| `snapshot/dead-N-crop-extraction/`, `dead-N-crop-prompts.json` | N-dead tight inference context removed gold rim; fringe not universally verified. |
| `snapshot/generation/layer-browser-review.json`, `check-layer-browser.cjs` | Actual3players/48frames, composition, timing, real controls,0network/errors. Script has original workspace paths; rebase in scratch. |
| `snapshot/generation/player-control-review.json`, `check-player-controls.py` | Four real incorrect player inputs rejected before output. |
| Other candidate folders' JSON | Prior iterations, failed contact/bob, prompt corrections, native blank-cel failure, timeout, missing native export destination; receipts retained, most duplicated image payloads omitted. Exact imagegen raw remains in raw/. |
| `snapshot/checkpoint.md`, `generation/checkpoint-live.md`, `model-provenance.json` | HISTORICAL stage notes/counters only. Cost question resolved;30generation jobs; current fringe failure supersedes early head claims. |

## Repository-level files outside this case

- **Root `CURRENT_HANDOFF.md`** points here and marks previous entries historical.
- **Root `tools/sprite-head-mask.py`, `sprite-head-ownership.py`, `sprite-layer-player.py`, `sprite-native-package.py`** are the4 new reusable tools committed with this transfer.
- **Root `tools/sprite-review-pack.py`, `whole-body-toolchain.py`, `sprite-motion-review.py` and contact tools** are existing, unchanged dependencies.
- **Root `.agents/skills/astraeon-whole-body-workflow/SKILL.md`** routes the3 installed requested skills. No new skill installation needed for transfer.
- **`../core-family-v56/frames/idle/`** is the original8view neutral source authority; frozen v56 catalog remains a provenance source, not current art approval.
- **`../ro-motion-lab-v51`, `../ro-core-views-v52`, `../ro-core-motion-v53`, `../unarmed-motion-v57`** hold external refs/source rigs; prior renderers are guides only.
- **`../whole-body-v58`, `../toolchain-study-v59`, `../free-local-repair-v60`** explain architecture, installed free tooling and prior failed repair. Frozen.
- **Root `AGENTS.md`, `HANDOFF.md` and all published <=v60/W13** are unchanged. They may have older top notes; CURRENT_HANDOFF governs current transfer.

## Not transferred

Installed `work/free-mask-model/env`, model/source clone,39MiB checkpoint, compiled Aseprite/build sources, SPA venv, browser installation, repeated ready/walk exposure PNGs, most obsolete raster intermediates, native re-export PNG duplicates and duplicate large review HTMLs. No credentials/account data. Rebuild runtimes from pinned receipts; derive repeated current exposures with restore helper. Native files, raw generation outputs, masks, keys, GIFs,3offline players and original check receipts are included.
