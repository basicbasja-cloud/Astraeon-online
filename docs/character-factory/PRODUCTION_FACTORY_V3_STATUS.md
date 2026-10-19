# Production Factory V3 status

**Branch:** `character/production-factory-v3`

**Base:** `a2e84a92b102f3cd91cc291a3425b8d6fdc0b8bb` (`character/production-factory-v2`)

**Candidate:** Male Swordsman

**Art state:** `DEV_ONLY / NOT_APPROVED`

## Completed in this checkpoint

- Audited V2 and donor research; recorded what V3 keeps, adapts, rejects, and supersedes in `PRODUCTION_FACTORY_V3.md`.
- Added a reusable 60-bone rig specification, identity lock, six-action config, semantic event contract, provenance registry, deterministic cache key, motion intake, and frame-sampling helper.
- Built an action-free V3 `.blend` copy of the V2 mannequin source. Blender 5.2.2 verified all 60 expected bones and removed all 17 old V2 actions. The generated scene contains zero actions.
- Rendered and checked the static rest-pose rig smoke in eight real camera directions with RGB, silhouette, depth, normal, body segmentation, and weapon mask passes. The passes are 320×320 RGBA and hash-pinned. A full contact sheet and 160×160 game-scale contact sheet are available.
- Added a deterministic waiting paint-job record with the locked identity, palette, six target layers, semantic event names, blockers, and a clearly labeled static review reference. It contains no false per-frame paint guide or painted output.
- Added automated tests for contracts, hash/license gates, sampling, path safety, and guide QA.

## Acceptance gates

| Gate | Status | Evidence |
|---|---|---|
| A — Canonical rig validates | **Pass** | 60-bone V3 rig manifest; 0 remaining actions. |
| B — New Idle/Walk/BasicAttack | **Blocked** | No external motion files have been acquired. V2 actions are disallowed. |
| C — Provenance/license | **Blocked** | Candidate records exist; provider files and retained license evidence are pending. |
| D — Retarget | Not run | Source skeleton and explicit bone map are unavailable. |
| E — Motion quality | Not run | No motion previews or candidate comparison exist. |
| F — Eight directions | **Static smoke pass** | Eight real camera yaws render; animated coverage is pending motions. |
| G — Structural passes | **Static smoke pass** | Six registered passes validate for each static direction; animated passes are pending. |
| H — Paint handoff | **Blocked** | Deterministic blocked record exists; no production animation guides exist. Static guides are rejected by the paint provider. |
| I — Modular painted output | Not run | No V3 painted layers exist. |
| J — Runtime package | Not run | No V3 painted strips exist to feed through the V2 packer/schema. |
| K — Astraeon preview | Not run | No V3 runtime package exists. |

## Motion acquisition request

The first candidates are MoCap Online's free Motion Sampler and free T.C. Sword pack. The user was asked to download the original ZIPs and license/receipt, then upload them under:

`authoring/characters/factory-v3/motions/inbox/`

Requested format: **FBX**. Do not send credentials. MoCap Online's Standard License requires prior written permission for AI use; the current paint stage is a manual handoff and no motion data may be sent to an AI provider without that permission. Raw motion files and checkout receipts are gitignored. Provenance and non-sensitive license evidence must be retained.

Rokoko candidates are listed as Tier 2 and have not been attempted. MoCap Online is the owner's preferred source; candidate selection still requires the actual files, provenance, license review, and visual comparison.

## Checks run

```text
python -m unittest discover -s tests/character_factory_v3 -v  — 10 tests passed
python -m py_compile tools/character_factory_v3/*.py tools/character_factory_v3/blender/*.py  — passed
run.py --stage rig-review --blender Blender 5.2.2  — static QA passed
run.py --stage all --blender Blender 5.2.2  — expected blocker exit 2 (no approved V3 motions)
```

## Continue

After the owner uploads the files and license evidence, complete provenance records using `authoring/characters/factory-v3/motions/provenance-template.json`, inspect the source skeleton, and define its explicit bone mapping. Source-specific FBX import/retarget, cleanup/stylization, and production animation rendering are not implemented yet; those stages need to be built and validated against the acquired skeleton before the vertical slice can continue. The current source-specific map is not guessed. No V3 action is selected or visually accepted.

This status does not claim a completed golden motion set, owner art approval, or in-game proof.

## Static rig review

- [Eight-direction contact sheet](../../authoring/characters/factory-v3/review/rig-smoke-5852ddaa72ba/contact-sheet.png)
- [160×160 game-scale contact sheet](../../authoring/characters/factory-v3/review/rig-smoke-5852ddaa72ba/game-scale-contact-sheet.png)
