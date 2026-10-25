# Canonical rig and visible Mage pilot — 25 October 2026

This is a production checkpoint, not the final six-character delivery.

## Inspect

- `mage-castrelease-once.gif`: sixteen painted NE poses, one-shot playback.
- `index.html`: actual separated-sheet compositor; use a local HTTP server.
- `browser-report.json`: 32 actual Chromium comparisons, zero changed pixels/page errors.
- `browser.png`: source and composed draft.

## Reproduce

From repository root:

```sh
python tools/character_factory_v3/package_visible_pilot_parts.py \
  --source authoring/characters/factory-v3/patch-0.0.1/review/mage-canonical-visible-cutouts-v6-20261025 \
  --masters authoring/characters/factory-v3/patch-0.0.1/painted-candidates/mage-canonical-planted-boots-v2-20261025/frames/Master \
  --output .factory-replay/mage-visible-parts-new
python tools/character_factory_v3/capture_visible_pilot_browser.py \
  --review docs/character-factory/review/patch001-canonical-mage-reuse-20261025
```

The raw illustrated sheet, source viewport and normalization recipe are frozen under `painted-candidates/mage-canonical-native-fingers-whole-20261024`. Image generation itself is not deterministic; the frozen-input factory replay is. Exact replay of 122 files is recorded in `research/canonical-rig-runtime-20261024/mage-visible-parts-frozen-input-replay-20261025.json`.

Native source/target captures are separate research outputs with exact script snapshots. Target captures require Blender 5.2.2; original source skeleton export uses 4.3.2. `verify_canonical_pilot.py` checks frozen input digests, captured PNGs, native samples, rotation/floor tolerances, cross-camera prop identity and arrow visibility.

## Open gates

Only two old Swordsman action jobs are registered. This Mage pilot is one direction of one action. Hidden head/neck surfaces, independent hand/staff ownership, alternate equipment, all other poses and actual game admission are unfinished. Empty FX slots are placeholders, not authored effects. The complete patch remains 94 imported jobs short; zero newly complete playable characters.
