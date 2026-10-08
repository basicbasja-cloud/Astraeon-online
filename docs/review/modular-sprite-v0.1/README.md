# Modular sprite foundation evidence

Base: `codex/world-pipeline-v3-proof` at
`a3b65899dd85666902a9115cbc400be9fb407525`.
Implementation branch: `codex/modular-sprite-pipeline-v0.1`.

Local fetch/ancestry verified that `Char-building` at `d7f9f15` is an ancestor
of the selected world base, with no unique commits. Its character work is
preserved in the base. The world branch has 49 commits beyond its merge-base with
main, and 13 beyond Char-building, including newer world renderer/streaming work.
Main's unique commit is its prior world-branch merge. Source branches are untouched.

The source/runtime contract, authoring commands and artwork insertion points are
in [MODULAR_SPRITES.md](../../MODULAR_SPRITES.md). The exact added/modified file
inventory is [files.json](files.json); machine-readable findings are
[summary.json](summary.json).

Verification passed:

- 96 existing and 34 new individual Node checks: `node-tests.json`, `modular-unit.tap`.
- Five existing streaming checks: `streaming-unit.tap`.
- Six Python normalization/packing/schema/pixel negative checks.
- Two definitions, 126 RGBA atlases and 3,024 part-frame references: full schema,
  shared runtime semantics, image dimensions, transparency and gutter validation.
- 432 real-browser poses, part swaps, playback, sockets, and responsive preview:
  `preview-browser.json` plus four preview captures.
- Ordinary movement/attack, original player retention, registered modular proof
  through the existing WebGL **2D** actor assembly, and preview/offline entry-page
  isolation: `runtime-browser.json`.
- Existing cache migration, saved-character recovery and offline original game
  reload: `cache-resume.json`. An initial cache version-list error was repaired
  before the passing rerun.
- Existing world JSON schemas, new/changed script syntax and `git diff --check`.
  This static project has no npm/package.json build step; the actual game launched.

Commands were run from the checkout with a static server on localhost:8011:

```sh
python3 tools/run-node-checks.py --output /tmp/astraeon-sprite-final-node
node --test --test-isolation=none --test-reporter=tap tests/world_streaming.test.mjs
python3 tools/validate-world-v3.py
python3 tools/validate-sprites.py
python3 tests/modular_sprite_tools.py
python3 tests/modular_sprite_browser.py --url http://127.0.0.1:8011
python3 tests/modular_runtime_browser.py --url http://127.0.0.1:8011
python3 tests/cache_resume.py --url http://127.0.0.1:8011
```

The captures were visually inspected for a shared ground root, visible separate
markers, correctly placed socket overlays and readable controls. They are clearly
labeled development geometry. They do not approve painted character anatomy,
weapons, costumes, camera or gait. Normal gameplay still uses its original painted
characters; these markers require explicit development opt-in.

Follow-up: confirm the existing Warrior identity's Swordsman mapping, supply the
approved Mage design, author shared directional masters and modular strips from
those sources, then review actual sole travel/body motion and equipment appearances
in-game. No production artwork approval or merging is performed by this branch.
